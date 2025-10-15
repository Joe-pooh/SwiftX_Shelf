from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()
_engine = None
_Session = None

def init_db(db_url: str):
    global _engine, _Session
    _engine = create_engine(db_url, echo=False, future=True)
    _Session = sessionmaker(bind=_engine, future=True)
    # import models and create tables
    from .models import Bins, Packages, ScanLogs  # noqa
    Base.metadata.create_all(_engine)

def get_session():
    return _Session()

def now_ts():
    return datetime.now(timezone.utc)
