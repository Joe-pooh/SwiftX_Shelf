import os, io, csv
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import init_db, get_session
from .models import User, Bins, Packages, ScanLogs
from .security import hash_password, verify_password, make_token, decode_token
from datetime import datetime, timezone
from contextlib import contextmanager
import qrcode

DB_URL = os.environ.get("DB_URL", "sqlite:///./shelf.db")
init_db(DB_URL)

app = FastAPI(title="Shelfing Cloud API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@contextmanager
def session_scope():
    s = get_session()
    try:
        yield s
    finally:
        s.close()

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
with session_scope() as s:
    exists = s.execute(select(User).where(User.username == ADMIN_USERNAME)).scalar_one_or_none()
    if not exists:
        u = User(username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD), role="admin")
        s.add(u); s.commit()

class LoginIn(BaseModel):
    username: str
    password: str

def get_current_user(request: Request) -> User:
    auth = request.headers.get("Authorization", "")
    token = None
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1].strip()
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Unauthorized")
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(401, "Invalid token")
    with session_scope() as s:
        u = s.get(User, int(payload["sub"]))
        if not u:
            raise HTTPException(401, "User not found")
        return u

@app.post("/auth/login")
def login(payload: LoginIn, response: Response):
    with session_scope() as s:
        u = s.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
        if not u or not verify_password(payload.password, u.password_hash):
            raise HTTPException(401, "Bad credentials")
        token = make_token(u.id, u.username, u.role)
        response.set_cookie("access_token", token, httponly=True, samesite="Lax")
        return {"token": token, "user": {"id": u.id, "username": u.username, "role": u.role}}

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"ok": True}

@app.get("/auth/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "role": user.role}

class BinIn(BaseModel):
    code: str

class PackageIn(BaseModel):
    tracking: str

class PutawayIn(BaseModel):
    bin_code: str
    tracking: str

class PickIn(BaseModel):
    tracking: str

def now_ts():
    return datetime.now(timezone.utc)

@app.get("/qr.png")
def qr_png(text: str, size: int = 256):
    img = qrcode.make(text)
    img = img.resize((size, size))
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    return StreamingResponse(bio, media_type="image/png")

@app.post("/bins")
def create_bin(payload: BinIn, user: User = Depends(get_current_user)):
    code = payload.code.strip().upper()
    if not code:
        raise HTTPException(400, "bin code required")
    with session_scope() as s:
        b = Bins(code=code)
        s.add(b)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            raise HTTPException(409, "bin already exists")
        return {"code": code}

@app.post("/packages")
def create_package(payload: PackageIn, user: User = Depends(get_current_user)):
    tracking = payload.tracking.strip().upper()
    if not tracking:
        raise HTTPException(400, "tracking required")
    with session_scope() as s:
        p = Packages(tracking=tracking, status="RECEIVED")
        s.add(p)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            return {"tracking": tracking, "status": "EXISTS"}
        return {"tracking": tracking, "status": "RECEIVED"}

@app.post("/putaway")
def putaway(payload: PutawayIn, user: User = Depends(get_current_user)):
    bin_code = payload.bin_code.strip().upper()
    tracking = payload.tracking.strip().upper()
    with session_scope() as s:
        bin_row = s.get(Bins, bin_code)
        if not bin_row:
            raise HTTPException(404, "bin not found")
        pkg = s.get(Packages, tracking)
        if not pkg:
            pkg = Packages(tracking=tracking, status="RECEIVED")
            s.add(pkg); s.flush()
        from_bin = pkg.bin_code
        pkg.bin_code = bin_code
        pkg.status = "STORED"
        pkg.last_scan_at = now_ts()
        log = ScanLogs(action="PUTAWAY", tracking=tracking, from_bin=from_bin, to_bin=bin_code, ok=True, reason=None, user=user.username)
        s.add(log); s.commit()
        return {"tracking": tracking, "bin_code": bin_code, "status": "STORED"}

@app.post("/pick")
def pick(payload: PickIn, user: User = Depends(get_current_user)):
    tracking = payload.tracking.strip().upper()
    with session_scope() as s:
        pkg = s.get(Packages, tracking)
        if not pkg:
            raise HTTPException(404, "package not found")
        from_bin = pkg.bin_code
        pkg.status = "PICKED"; pkg.bin_code = None; pkg.last_scan_at = now_ts()
        log = ScanLogs(action="PICK", tracking=tracking, from_bin=from_bin, to_bin=None, ok=True, reason=None, user=user.username)
        s.add(log); s.commit()
        return {"tracking": tracking, "status": "PICKED", "from_bin": from_bin}

@app.get("/packages/{tracking}")
def get_package(tracking: str, user: User = Depends(get_current_user)):
    with session_scope() as s:
        pkg = s.get(Packages, tracking.upper())
        if not pkg:
            raise HTTPException(404, "package not found")
        return {
            "tracking": pkg.tracking,
            "status": pkg.status,
            "bin_code": pkg.bin_code,
            "first_in_at": pkg.first_in_at.isoformat() if pkg.first_in_at else None,
            "last_scan_at": pkg.last_scan_at.isoformat() if pkg.last_scan_at else None,
        }

@app.get("/export/scan_logs")
def export_scan_logs(user: User = Depends(get_current_user)):
    with session_scope() as s:
        rows = s.execute(select(ScanLogs).order_by(ScanLogs.ts.asc())).scalars().all()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["ts","user","action","tracking","from_bin","to_bin","ok","reason"])
    for r in rows:
        w.writerow([r.ts.isoformat(), r.user or "", r.action or "", r.tracking or "", r.from_bin or "", r.to_bin or "", "1" if r.ok else "0", r.reason or ""])
    output.seek(0)
    return StreamingResponse(iter([output.read()]), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=scan_logs.csv"})
