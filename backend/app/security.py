import os, time
from passlib.context import CryptContext
from jose import jwt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGO = "HS256"
SECRET = os.environ.get("JWT_SECRET", "dev-secret-change")
TOKEN_TTL = 60*60*12  # 12h

def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)

def make_token(user_id: int, username: str, role: str) -> str:
    now = int(time.time())
    payload = {"sub": str(user_id), "username": username, "role": role, "iat": now, "exp": now + TOKEN_TTL}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token: str):
    return jwt.decode(token, SECRET, algorithms=[ALGO])
