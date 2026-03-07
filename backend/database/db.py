from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.config import settings

# Since we are using SQLite asynchronously, ensure the URL uses the aiosqlite driver
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} # Needed for SQLite
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """
    Dependency to provide a database session per request.
    """
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """
    Creates all tables in the database.
    (In production, you'd use Alembic migrations instead)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
