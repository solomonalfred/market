from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from source.constants import Endpoints, RouterInfo
from source.db import get_async_session
from source.db.models import User
from source.db.user_methods import get_user_history, purchase_item, transfer_coins
from source.routers.auth.services import get_current_user
from source.routers.shemas.user import ItemInfo, ResponseMessage, SendCoin, UserHistory

router = APIRouter(prefix=RouterInfo.prefix, tags=[RouterInfo.user_tags])


@router.get(
    path=Endpoints.INFO,
    response_model=UserHistory,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о монетах, инвентаре и истории транзакций.",
)
async def info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    try:
        history = await get_user_history(db, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    return history


@router.post(
    path=Endpoints.SEND_COINS,
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Отправить монеты другому пользователю.",
)
async def send_coin(
    current_user: Annotated[User, Depends(get_current_user)],
    transaction: SendCoin,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    try:
        result = await transfer_coins(db, current_user, transaction)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера.",
        )
    if not result:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"description": "Недостаточно средств."},
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"description": "Успешный ответ."})


@router.get(
    path=Endpoints.BUY,
    response_model=ResponseMessage,
    status_code=status.HTTP_200_OK,
    summary="Купить предмет за монеты.",
)
async def buy(
    current_user: Annotated[User, Depends(get_current_user)],
    item: str,
    db: AsyncSession = Depends(get_async_session),
) -> Any:
    try:
        result = await purchase_item(db, current_user, ItemInfo(name=item))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера.",
        )
    if result:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"description": "Успешный ответ."})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"description": "Недостаточно средств."},
    )
