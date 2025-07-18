from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast1.settings import Settings

engine = create_engine(Settings().DATABASE_URL)


# pragma: no cover
def get_session():
    with Session(engine) as session:
        yield session
