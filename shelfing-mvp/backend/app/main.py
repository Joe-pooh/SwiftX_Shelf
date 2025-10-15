import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from .db import get_session, init_db, now_ts
from .models import Bins, Packages, ScanLogs
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
import io
import csv

DB_URL = os.environ.get("DB_URL", "postgresql://app:app@localhost:5432/shelf")
init_db(DB_URL)

app = FastAPI(title="Shelfing MVP API", version="0.1.0")

# CORS: allow all for MVP; tighten later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BinIn(BaseModel):
    code: str

class PackageIn(BaseModel):
    tracking: str

class PutawayIn(BaseModel):
    bin_code: str
    tracking: str

class PickIn(BaseModel):
    tracking: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/bins")
def create_bin(payload: BinIn):
    code = payload.code.strip().upper()
    if not code:
        raise HTTPException(400, "bin code required")
    with get_session() as s:
        b = Bins(code=code)
        s.add(b)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            raise HTTPException(409, "bin already exists")
        return {"code": code}

@app.post("/packages")
def create_package(payload: PackageIn):
    tracking = payload.tracking.strip().upper()
    if not tracking:
        raise HTTPException(400, "tracking required")
    with get_session() as s:
        p = Packages(tracking=tracking, status="RECEIVED")
        s.add(p)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            # already exists is OK for idempotency
            return {"tracking": tracking, "status": "EXISTS"}
        return {"tracking": tracking, "status": "RECEIVED"}

@app.post("/putaway")
def putaway(payload: PutawayIn):
    bin_code = payload.bin_code.strip().upper()
    tracking = payload.tracking.strip().upper()
    with get_session() as s:
        bin_row = s.get(Bins, bin_code)
        if not bin_row:
            raise HTTPException(404, "bin not found")
        pkg = s.get(Packages, tracking)
        if not pkg:
            # auto-create on first scan (MVP behavior)
            pkg = Packages(tracking=tracking, status="RECEIVED")
            s.add(pkg)
            s.flush()
        from_bin = pkg.bin_code
        pkg.bin_code = bin_code
        pkg.status = "STORED"
        pkg.last_scan_at = now_ts()
        log = ScanLogs(
            action="PUTAWAY",
            tracking=tracking,
            from_bin=from_bin,
            to_bin=bin_code,
            ok=True,
            reason=None,
            user="demo",
        )
        s.add(log)
        s.commit()
        return {"tracking": tracking, "bin_code": bin_code, "status": "STORED"}

@app.post("/pick")
def pick(payload: PickIn):
    tracking = payload.tracking.strip().upper()
    with get_session() as s:
        pkg = s.get(Packages, tracking)
        if not pkg:
            raise HTTPException(404, "package not found")
        from_bin = pkg.bin_code
        pkg.status = "PICKED"
        pkg.bin_code = None
        pkg.last_scan_at = now_ts()
        log = ScanLogs(
            action="PICK",
            tracking=tracking,
            from_bin=from_bin,
            to_bin=None,
            ok=True,
            reason=None,
            user="demo",
        )
        s.add(log)
        s.commit()
        return {"tracking": tracking, "status": "PICKED", "from_bin": from_bin}

@app.get("/packages/{tracking}")
def get_package(tracking: str):
    with get_session() as s:
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
def export_scan_logs():
    with get_session() as s:
        rows = s.execute(select(ScanLogs).order_by(ScanLogs.ts.asc())).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ts","user","action","tracking","from_bin","to_bin","ok","reason"])
    for r in rows:
        writer.writerow([
            r.ts.isoformat() if r.ts else "",
            r.user or "",
            r.action or "",
            r.tracking or "",
            r.from_bin or "",
            r.to_bin or "",
            "1" if r.ok else "0",
            r.reason or "",
        ])
    output.seek(0)
    return StreamingResponse(iter([output.read()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=scan_logs.csv"})
