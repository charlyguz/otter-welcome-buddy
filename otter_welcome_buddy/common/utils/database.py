from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker


def get_cache_connection_string(db_path: str) -> str:
    """Returns the path to the database formatted as a sqlite connection"""
    return f"sqlite:///{db_path}"


def get_cache_engine(db_path: str) -> Engine:
    """Initializes the SQLAlchemy engine"""
    return create_engine(get_cache_connection_string(db_path=db_path))


def create_cache_session(db_path: str) -> Session:
    """Get a session to be used for transaction on the database"""
    engine = get_cache_engine(db_path=db_path)
    session_factory = sessionmaker(bind=engine)
    return session_factory()
