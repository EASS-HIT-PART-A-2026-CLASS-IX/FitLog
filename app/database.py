"""
Database initialization and connection management.
"""
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///fitlog.db")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_and_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get a database session."""
    async with async_session_maker() as session:
        yield session
