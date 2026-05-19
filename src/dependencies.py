from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from configuration import BATCH_COUNT, CONNECTION_STRING, TIME_WINDOW
from utils import parse_timedelta

engine = create_engine(CONNECTION_STRING, pool_pre_ping=True)

time_window = parse_timedelta(TIME_WINDOW)

batch_count = BATCH_COUNT

CreateSession = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    session = CreateSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
