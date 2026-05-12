from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configuration import CONNECTION_STRING, TIME_WINDOW, BATCH_COUNT
from utils import parse_timedelta

engine = create_engine(CONNECTION_STRING)

time_window = parse_timedelta(TIME_WINDOW)

batch_count = BATCH_COUNT

CreateSession = sessionmaker(bind=engine)