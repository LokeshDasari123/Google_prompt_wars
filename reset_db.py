from app.db.database import engine
from app.db import models
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Dropping all tables...")
models.Base.metadata.drop_all(bind=engine)
logger.info("Tables dropped successfully. The next app startup will recreate and re-seed them.")
