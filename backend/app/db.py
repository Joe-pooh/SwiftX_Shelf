from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
_engine = None
_Session = None

def init_db(db_url: str):
    global _engine, _Session
    _engine = create_engine(db_url, echo=False, future=True)
    _Session = sessionmaker(bind=_engine, future=True)
    from . import models
    Base.metadata.create_all(_engine)

def get_session():
    return _Session()
