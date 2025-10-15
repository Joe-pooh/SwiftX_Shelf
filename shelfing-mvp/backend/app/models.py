from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc)

class Bins(Base):
    __tablename__ = "bins"
    code: Mapped[str] = mapped_column(String(64), primary_key=True)

class Packages(Base):
    __tablename__ = "packages"
    tracking: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bin_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=True)
    last_scan_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class ScanLogs(Base):
    __tablename__ = "scan_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utcnow)
    user: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tracking: Mapped[str | None] = mapped_column(String(64), nullable=True)
    from_bin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    to_bin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ok: Mapped[bool | None] = mapped_column(Boolean, default=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
