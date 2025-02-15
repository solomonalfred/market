from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, update
from typing import Optional, List, Tuple
from source.utils import PasswordManager
from source.db.models import User, Purchase, Transaction, Merch
from source.routers.shemas.auth import Registration
from source.routers.shemas.user import UserHistory, SendCoin, ItemInfo
from source.routers.shemas.admin import AdminUser
from source.db.role_types import RoleType
from source.routers.shemas.admin import UpdateUser, MerchInfo

hashed = PasswordManager()

async def find_user_by_login(session: AsyncSession, login: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.login == login))
    user = result.scalars().one_or_none()
    return user

async def create_user(session: AsyncSession,
                      user_data: Registration | AdminUser) -> User:
    hashed_password = hashed.hash_password(user_data.password)
    coins = 0
    if isinstance(user_data, AdminUser):
        coins = user_data.coins_amount
    new_user = User(
        login=user_data.login,
        password_hash=hashed_password,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.role
    )
    new_user.coin_amount = coins
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

async def transfer_coins(session: AsyncSession,
                         sender: User,
                         transaction: SendCoin) -> bool:
    receiver = await find_user_by_login(session, transaction.toUser)
    if not sender or not receiver:
        return False
    if sender.coin_amount < transaction.amount:
        return False
    sender.coin_amount -= transaction.amount
    receiver.coin_amount += transaction.amount
    transaction = Transaction(from_user=sender.id, to_user=receiver.id, amount=transaction.amount)
    session.add(transaction)
    try:
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False

async def purchase_item(session: AsyncSession,
                        user: User,
                        merch_name: ItemInfo) -> bool:
    result = await session.execute(select(Merch).where(Merch.name == merch_name.name))
    merch = result.scalars().one_or_none()
    if not merch:
        return False

    if user.coin_amount < merch.price:
        return False

    user.coin_amount -= merch.price
    purchase = Purchase(user_id=user.id, merch_id=merch.id)
    session.add(purchase)
    try:
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False

async def get_user_history(session: AsyncSession, user: User) -> UserHistory:
    inventory_result = await session.execute(
        select(Merch.name, func.count(Purchase.merch_id))
        .join(Purchase, Purchase.merch_id == Merch.id)
        .where(Purchase.user_id == user.id)
        .group_by(Merch.name)
    )
    inventory: List[Tuple[str, int]] = inventory_result.all()
    received_result = await session.execute(
        select(User.login, Transaction.amount)
        .join(User, Transaction.from_user == User.id)
        .where(Transaction.to_user == user.id)
    )
    received: List[Tuple[str, int]] = received_result.all()
    sent_result = await session.execute(
        select(User.login, Transaction.amount)
        .join(User, Transaction.to_user == User.id)
        .where(Transaction.from_user == user.id)
    )
    sent: List[Tuple[str, int]] = sent_result.all()
    history = UserHistory(
        coins=user.coin_amount,
        inventory=inventory,
        coinHistory={"received": received, "sent": sent}
    )
    return history

async def add_merch(session: AsyncSession, data: MerchInfo) -> Optional[Merch]:
    result = await session.execute(select(Merch).where(Merch.name == data.name))
    existing_merch = result.scalars().one_or_none()
    if existing_merch:
        return None
    new_merch = Merch(name=data.name, price=data.price)
    session.add(new_merch)
    try:
        await session.commit()
        await session.refresh(new_merch)
        return new_merch
    except Exception:
        await session.rollback()
        return None

async def get_dummy_user(session: AsyncSession) -> User:
    dummy = await find_user_by_login(session, "[Deleted]")
    if not dummy:
        dummy = User(
            login="[Deleted]",
            password_hash=RoleType.deleted,  # заглушка для password_hash
            role=RoleType.deleted,
            coin_amount=0
        )
        session.add(dummy)
        await session.commit()
        await session.refresh(dummy)
    return dummy

async def delete_user_by_login(session: AsyncSession, login: str) -> bool:
    user = await find_user_by_login(session, login)
    if not user:
        return False
    dummy_user = await get_dummy_user(session)
    await session.execute(
        update(Transaction)
        .where(Transaction.from_user == user.id)
        .values(from_user=dummy_user.id)
    )
    await session.execute(
        update(Transaction)
        .where(Transaction.to_user == user.id)
        .values(to_user=dummy_user.id)
    )
    purchases_result = await session.execute(
        select(Purchase).where(Purchase.user_id == user.id)
    )
    purchases = purchases_result.scalars().all()
    for purchase in purchases:
        await session.delete(purchase)
    await session.delete(user)
    try:
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False

async def update_user(session: AsyncSession,
                      data: UpdateUser) -> bool:
    user = await find_user_by_login(session, data.login)
    if not user:
        return False
    user.coin_amount = data.coin_amount
    if data.role is not None:
        user.role = data.role
    else:
        user.role = RoleType.user
    try:
        await session.commit()
        return True
    except Exception:
        await session.rollback()
        return False
