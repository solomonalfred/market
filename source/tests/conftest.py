import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from source.db.models import Base


# pytest_plugins = ["pytest_postgresql"]

@pytest.fixture(scope='session')
def postgres_dsn(postgresql_proc):
    host = getattr(postgresql_proc, "host", "localhost")
    port = getattr(postgresql_proc, "port", "5433")
    user = "avito"
    dbname = "pytest"
    password = "12345"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"

test_async_engine = None

@pytest_asyncio.fixture(scope="session")
async def async_engine(postgres_dsn):
    engine = create_async_engine(postgres_dsn, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    global test_async_engine
    test_async_engine = engine
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

async def override_get_async_session():
    AsyncSessionTesting = sessionmaker(
        test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with test_async_engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSessionTesting(bind=connection) as session:
            yield session
        await transaction.rollback()
