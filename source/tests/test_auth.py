from contextlib import asynccontextmanager
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
import sys
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from source.app import app
from source.db import get_async_session
from source.db.models import Base
from source.tests.conftest import override_get_async_session

# @pytest.fixture
@pytest_asyncio.fixture
async def client(async_engine):
    # Определяем переопределение зависимости, используя переданный async_engine
    async def _override_get_async_session():
        AsyncSessionTesting = sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        async with async_engine.connect() as connection:
            transaction = await connection.begin()
            async with AsyncSessionTesting(bind=connection) as session:
                yield session
            await transaction.rollback()

    # Устанавливаем переопределение зависимости перед созданием клиента
    app.dependency_overrides[get_async_session] = _override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_example(client: AsyncClient):
    response = await client.get("/ping")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_registration(client: AsyncClient):
    payload = {
        "login": "testdup",
        "password": "testpass123",
        "email": "dup@example.com",
        "first_name": "Dup",
        "last_name": "User"
    }
    response1 = await client.post("/api/signup", json=payload)
    assert response1.status_code == 200, response1.text

@pytest.mark.asyncio
async def test_duplicate_registration(client: TestClient):
    payload = {
        "login": "testdup",
        "password": "testpass123",
        "email": "dup@example.com",
        "first_name": "Dup",
        "last_name": "User"
    }
    response1 = await client.post("/api/auth/signup", json=payload)
    assert response1.status_code == 200, response1.text
    response2 = await client.post("/api/auth/signup", json=payload)
    assert response2.status_code == 400, response2.text
    data2 = response2.json()
    assert data2.get("detail") == "Пользователь с таким логином уже существует"

@pytest.mark.asyncio
async def test_token(client: TestClient):
    payload = {
        "login": "testtoken",
        "password": "testpass123",
        "email": "token@example.com",
        "first_name": "Token",
        "last_name": "User"
    }
    response = await client.post("/api/auth/signup", json=payload)
    assert response.status_code == 200, response.text
    form_data = {
        "username": "testtoken",
        "password": "testpass123"
    }
    response_token = await client.post("/api/auth/token", data=form_data)
    assert response_token.status_code == 200, response_token.text
    token_data = response_token.json()
    assert "access_token" in token_data

@pytest.mark.asyncio
async def test_admin_token(client: TestClient):
    form_data = {
        "username": "admin",
        "password": "123456"
    }
    response_token = client.post("/api/auth/token", data=form_data)
    assert response_token.status_code == 200, response_token.text
    token_data = response_token.json()
    assert "access_token" in token_data
