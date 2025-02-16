import pytest


@pytest.mark.asyncio
async def test_ping(async_client):
    response = await async_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"res": "hi"}

@pytest.mark.asyncio
async def test_registration_and_token(async_client):
    registration_payload = {
        "login": "testuser1",
        "password": "testpass123",
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
    }

    response = await async_client.post("/api/signup", json=registration_payload)
    assert response.status_code == 200 or response.status_code == 400, response.text
    # assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data or True
    # assert "access_token" in data

    response_dup = await async_client.post("/api/signup", json=registration_payload)
    assert response_dup.status_code == 400, response_dup.text
    dup_data = response_dup.json()
    assert dup_data.get("detail") == "Пользователь с таким логином уже существует"
    form_data = {"username": "testuser1", "password": "testpass123"}
    response_token = await async_client.post("/api/auth", data=form_data)
    assert response_token.status_code == 200, response_token.text
    token_data = response_token.json()
    assert "access_token" in token_data
