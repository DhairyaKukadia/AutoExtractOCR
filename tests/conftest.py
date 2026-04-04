from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data.database import Base


def make_test_session():
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSession()
