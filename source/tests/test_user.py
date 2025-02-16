# import pytest
# from httpx import AsyncClient
# import sys
# import os
#
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# from source.app import app
# from source.db import get_async_session
# from source.routers.auth import get_current_user
#
#
# class DummyUser:
#     data = "testuser"
#     role = "user"
#
# @pytest.fixture(autouse=True)
# def override_get_current_user():
#     async def dummy_get_current_user():
#         return DummyUser()
#     app.dependency_overrides[get_current_user] = dummy_get_current_user
#     yield
#     app.dependency_overrides.pop(get_current_user, None)
#
# @pytest.fixture
# async def client(async_session):
#     async def override_get_async_session():
#         yield async_session
#     app.dependency_overrides[get_async_session] = override_get_async_session
#     async with AsyncClient(app=app, base_url="http://testserver") as ac:
#         yield ac
#
#
# @pytest.mark.asyncio
# async def test_info_endpoint(client: AsyncClient, monkeypatch):
#     # Фиктивная реализация get_user_history
#     async def dummy_get_user_history(db, user):
#         return {
#             "coins": 100,
#             "inventory": [("sword", 1)],
#             "coinHistory": {"received": [("initial", 100)], "sent": []}
#         }
#     import source.routers.user.user as coin_endpoints
#     monkeypatch.setattr(coin_endpoints, "get_user_history", dummy_get_user_history)
#
#     response = await client.get("/info")
#     # assert response.status_code == 200
#     data = response.json()
#     print(data["coins"])
#     assert data["coins"] == 99
#     # В зависимости от сериализации, список кортежей может прийти как список списков
#     assert data["inventory"] == [["sword", 1]] or data["inventory"] == [("sword", 1)]
#     assert "coinHistory" in data
