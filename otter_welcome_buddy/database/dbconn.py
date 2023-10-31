from contextlib import contextmanager

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

from otter_welcome_buddy.common.constants import DATA_FILE_PATH
from otter_welcome_buddy.common.utils.database import create_cache_session


BaseModel = declarative_base()


@contextmanager
def cache_session_scope(db_path: str = DATA_FILE_PATH) -> Session:
    """
    Provide a transactional scope around a series of database operations.

    Parameters:
        db_path (str): Path to the SQLite database file.

    Yields:
        sqlalchemy.orm.session.Session: A SQLAlchemy session object.

    Raises:
        Any: Any exception that occurred during the execution of the block.
    """
    session = create_cache_session(db_path=db_path)
    try:
        yield session
        session.commit()
    except Exception as ex:
        print(f"Error while commiting the database changes: {ex}")
        session.rollback()
        raise
    finally:
        session.close()
