from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from source.constants import Endpoints, RouterInfo
from source.db import RoleType, create_user, find_user_by_login, get_async_session
from source.routers.auth.exception import credentials_exception
from source.routers.auth.services import authenticate_user, generate_token
from source.routers.shemas.auth import Credentials, Registration, Token

router = APIRouter(prefix=RouterInfo.prefix, tags=[RouterInfo.auth_tags])


@router.post(
    path=Endpoints.SIGNUP,
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Registration user",
)
async def registration(user_data: Registration, db: AsyncSession = Depends(get_async_session)) -> Any:
    try:
        user = await find_user_by_login(db, user_data.login)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя",
        )
    # user = await find_user_by_login(db, user_data.login)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует",
        )
    try:
        user_data.role = RoleType.user
        await create_user(db, user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании пользователя",
        )
    token = await generate_token({"data": user_data.login})
    return token


@router.post(
    path=Endpoints.TOKEN,
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Аутентификация и получение JWT-токена.",
)
async def token(
    user_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    try:
        user = await authenticate_user(Credentials(login=user_data.username, password=user_data.password), db)
        if not user:
            raise credentials_exception
        tokens = await generate_token({"data": user.login, "role": user.role})
        return tokens
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при авторизации",
        )
