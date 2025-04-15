import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine
from src.database.session import init_db

from src.database.models import Base
from src.config import get_settings
from database import reset_sqlite_database, get_db_contextmanager
from database.populate import CSVDatabaseSeeder
from main import app

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def initialize_db():
    await init_db()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_db_tables():
    await reset_sqlite_database()
    await create_tables()


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with get_db_contextmanager() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def seed_database(db_session):
    settings = get_settings()
    seeder = CSVDatabaseSeeder(
        csv_file_path=settings.PATH_TO_MOVIES_CSV, db_session=db_session
    )

    await seeder.seed()
    await db_session.commit()

    yield
