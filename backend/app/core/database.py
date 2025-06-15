from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

try:
    engine = create_engine(str(settings.DATABASE_URL))
    # Test the connection
    with engine.connect() as conn:
        pass
except OperationalError as e:
    logger.error(f"Failed to connect to database: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 