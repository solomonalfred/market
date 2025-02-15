from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Annotated
from source.constants import Endpoints, RouterInfo
from source.db import (
    get_async_session,
    create_user,
    add_merch,
    delete_user_by_login,
    update_user,
    RoleType
)
from source.db.models import User
from source.routers.auth.services import get_current_user
from source.routers.shemas.admin import AdminUser, MerchInfo, UpdateUser
from source.routers.shemas.user import ResponseMessage


router = APIRouter(prefix=RouterInfo.prefix,
                   tags=[RouterInfo.admin_tags])

@router.put(
    path=Endpoints.ADD_USER,
    response_model=ResponseMessage,
    status_code = status.HTTP_200_OK,
    summary = "Создание пользователя."
)
async def add_user(current_user: Annotated[User, Depends(get_current_user)],
                   user: AdminUser,
                   db: AsyncSession = Depends(get_async_session)) -> Any:
    if current_user.role != RoleType.admin:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"description": "Недостаточно прав."})
    try:
        await create_user(db, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера."
        )
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"description": "Успешный ответ."})

@router.put(
    path=Endpoints.ADD_MERCH,
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Добавление вещи."
)
async def add_merch_item(current_user: Annotated[User, Depends(get_current_user)],
                         item: MerchInfo,
                         db: AsyncSession = Depends(get_async_session)) -> Any:
    if current_user.role != RoleType.admin:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"description": "Недостаточно прав."})
    try:
        result = await add_merch(db, item)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера."
        )
    if result is None:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"description": "Товар уже существует."})
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"description": "Успешный ответ."})

@router.delete(
    path=Endpoints.DELETE_USER,
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Удаление пользователя."
)
async def delete_user(current_user: Annotated[User, Depends(get_current_user)],
                      login: str,
                      db: AsyncSession = Depends(get_async_session)) -> Any:
    if current_user.role != RoleType.admin:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"description": "Недостаточно прав."})
    try:
        result = await delete_user_by_login(db, login)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера."
        )
    if result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"description": "Пользователь уже не существует."})
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"description": "Успешный ответ."})

@router.post(
    path=Endpoints.UPDATE_USER,
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Обновление пользователя."
)
async def update_user_info(current_user: Annotated[User, Depends(get_current_user)],
                           data: UpdateUser,
                           db: AsyncSession = Depends(get_async_session)) -> Any:
    if current_user.role != RoleType.admin:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"description": "Недостаточно прав."})
    try:
        result = await update_user(db, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера."
        )
    if result:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"description": "Пользователь не существует."})
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"description": "Успешный ответ."})
