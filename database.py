from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:gai3905@localhost/Pokemon'

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency for getting the database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db  # This will be the database session used in routes
    finally:
        db.close()  # Ensure the session is closed after use
