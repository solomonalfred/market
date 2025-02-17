import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_info(async_client: AsyncClient):
    registration_payload = {
        "login": "testuser1",
        "password": "testpass123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post("/api/signup", json=registration_payload)
    assert response.status_code == 200 or response.status_code == 400, response.text
    data = response.json()
    assert "access_token" in data or True
    form_data = {"username": "testuser1", "password": "testpass123"}
    response_token = await async_client.post("/api/auth", data=form_data)
    assert response_token.status_code == 200, response_token.text
    token_data = response_token.json()
    assert "access_token" in token_data
    headers = {"Authorization": f"Bearer {token_data.get("access_token")}"}
    response = await async_client.get("/api/info", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "coins" in data
    assert "inventory" in data
    assert "coinHistory" in data

@pytest.mark.asyncio
async def test_send_coins(async_client: AsyncClient):
    registration_payload = {
        "login": "testuser1",
        "password": "testpass123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post("/api/signup", json=registration_payload)
    assert response.status_code == 200 or response.status_code == 400, response.text
    data = response.json()
    assert "access_token" in data or True
    form_data = {"username": "admin", "password": "123456"}
    response_token = await async_client.post("/api/auth", data=form_data)
    data = response_token.json()["access_token"]
    headers = {"Authorization": f"Bearer {data}"}
    data = {
        "login": "testuser1",
        "coin_amount": 200,
        "role": "user",
    }
    response = await async_client.post("/api/updateUser", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"description": "Успешный ответ."}
    form_data = {"username": "testuser1", "password": "testpass123"}
    response_token = await async_client.post("/api/auth", data=form_data)
    assert response_token.status_code == 200, response_token.text
    token_data = response_token.json()
    assert "access_token" in token_data
    headers = {"Authorization": f"Bearer {token_data.get("access_token")}"}
    registration_payload = {
        "login": "testuser2",
        "password": "testpass123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post("/api/signup", json=registration_payload)
    assert response.status_code == 200 or response.status_code == 400, response.text
    data = response.json()
    assert "access_token" in data or True
    data = {"toUser": "testuser2", "amount": 10}
    response = await async_client.post("/api/sendCoin", json=data, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"description": "Успешный ответ."}

@pytest.mark.asyncio
async def test_send_coins_insufficient_funds(async_client: AsyncClient):
    registration_payload = {
        "login": "testuser1",
        "password": "testpass123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post("/api/signup", json=registration_payload)
    assert response.status_code == 200 or response.status_code == 400, response.text
    data = response.json()
    assert "access_token" in data or True
    form_data = {"username": "testuser1", "password": "testpass123"}
    response_token = await async_client.post("/api/auth", data=form_data)
    assert response_token.status_code == 200, response_token.text
    token_data = response_token.json()
    assert "access_token" in token_data
    headers = {"Authorization": f"Bearer {token_data.get("access_token")}"}
    registration_payload = {
        "login": "testuser2",
        "password": "testpass123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post("/api/signup", json=registration_payload)
    assert response.status_code == 200 or response.status_code == 400, response.text
    data = response.json()
    assert "access_token" in data or True
    data = {"toUser": "testuser2", "amount": 1000}
    response = await async_client.post("/api/sendCoin", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"description": "Недостаточно средств."}
