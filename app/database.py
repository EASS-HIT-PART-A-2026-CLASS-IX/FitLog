"""
Database initialization and connection management with performance optimizations.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import settings

DATABASE_URL = settings.database_url

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        connect_args={
            "timeout": 15,
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Enable WAL mode for concurrent reads (SQLite only)
        if is_sqlite:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL")
            await conn.exec_driver_sql("PRAGMA synchronous=NORMAL")
            await conn.exec_driver_sql("PRAGMA cache_size=-64000")
            await conn.exec_driver_sql("PRAGMA temp_store=MEMORY")
        await conn.run_sync(SQLModel.metadata.create_all)
        # Migrate old databases that are missing profile_id columns
        await conn.run_sync(_migrate_add_profile_id)


def _migrate_add_profile_id(sync_conn):
    """Add profile_id column and index to existing tables if missing."""
    result = sync_conn.exec_driver_sql("PRAGMA table_info(workout_logs)")
    columns = [row[1] for row in result.fetchall()]
    if "profile_id" not in columns:
        sync_conn.exec_driver_sql(
            "ALTER TABLE workout_logs ADD COLUMN profile_id VARCHAR"
        )
        sync_conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_workout_logs_profile_id ON workout_logs(profile_id)"
        )

    result = sync_conn.exec_driver_sql("PRAGMA table_info(macro_entries)")
    columns = [row[1] for row in result.fetchall()]
    if "profile_id" not in columns:
        sync_conn.exec_driver_sql(
            "ALTER TABLE macro_entries ADD COLUMN profile_id VARCHAR"
        )
        sync_conn.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS ix_macro_entries_profile_id ON macro_entries(profile_id)"
        )


async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session_maker() as session:
        yield session
