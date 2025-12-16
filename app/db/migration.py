import logging
from pathlib import Path

from alembic.config import Config

from alembic import command

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Run Alembic migrations to upgrade the database to the latest version.

    This function will:
    - Initialize all tables if the database is empty
    - Apply pending migrations if the database already exists
    """
    try:
        # Get the project root directory (parent of app/)
        project_root = Path(__file__).parent.parent.parent
        alembic_ini_path = project_root / "alembic.ini"

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini_path))

        # Run migrations to the latest version
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")

    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise
