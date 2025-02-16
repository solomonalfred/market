from typing import Annotated, Optional

import sqlalchemy as sql
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Session, relationship, sessionmaker
from typing_extensions import AsyncGenerator

from source.config import get_settings

MetaStr = Annotated[str, 255]
DetailedInfoStr = Annotated[str, 2000]
ends, tab = "\n", "\t"


@as_declarative()
class Base:
    __table_args__ = {"extend_existing": True}

    type_annotation_map = {MetaStr: String(255), DetailedInfoStr: String(2000)}

    def __repr__(self):
        columns = []
        for column in self.__table__.columns.keys():
            columns.append(f"{column}={getattr(self, column)}")
        return f"[{self.__class__.__name__}]{ends}{tab}{f',{ends + tab}'.join(columns)}"

    id = Column(Integer, primary_key=True, index=True)


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        CheckConstraint("coin_amount >= 0", name="user_coin_amount_nonnegative"),
        {"extend_existing": True},
    )

    login: Annotated[str, 150] = Column(String(150), nullable=False, unique=True)
    password_hash: Annotated[str, 255] = Column(String(255), nullable=False)
    # is_enable: bool = Column(Boolean, nullable=False, default=True)
    email: Optional[str] = Column(String(255), nullable=True)
    first_name: Optional[str] = Column(String(64), nullable=True)
    last_name: Optional[str] = Column(String(64), nullable=True)
    role: Annotated[str, 64] = Column(String(64), nullable=False, default="user")
    coin_amount: int = Column(Integer, nullable=False, default=0, server_default="0")

    sent_transactions = relationship(
        "Transaction", foreign_keys="[Transaction.from_user]"
    )
    received_transactions = relationship(
        "Transaction", foreign_keys="[Transaction.to_user]"
    )
    purchases = relationship("Purchase", back_populates="user")


class Merch(Base):
    __tablename__ = "merch"
    __table_args__ = (
        CheckConstraint("price >= 0", name="merch_price_nonnegative"),
        {"extend_existing": True},
    )

    name: Annotated[str, 255] = Column(String(255), nullable=False, unique=True)
    price: int = Column(Integer, nullable=False, default=0, server_default="0")
    purchases = relationship("Purchase", back_populates="merch")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="transaction_amount_nonnegative"),
        {"extend_existing": True},
    )

    from_user: int = Column(Integer, ForeignKey("user.id"), nullable=False)
    to_user: int = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount: int = Column(Integer, nullable=False)
    sender = relationship("User", foreign_keys=[from_user])
    receiver = relationship("User", foreign_keys=[to_user])


class Purchase(Base):
    __tablename__ = "purchases"
    __table_args__ = {"extend_existing": True}

    user_id: int = Column(Integer, ForeignKey("user.id"), nullable=False)
    merch_id: int = Column(Integer, ForeignKey("merch.id"), nullable=False)
    user = relationship("User", back_populates="purchases")
    merch = relationship("Merch", back_populates="purchases")


class SessionManager:
    def __init__(self):
        settings = get_settings()
        self.async_engine = create_async_engine(url=settings.DB_URI, echo=False)

        self.async_session = sessionmaker(
            self.async_engine, expire_on_commit=False, class_=AsyncSession
        )

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def get_session(self) -> Session | AsyncSession:
        return self.async_session()

    async def get_table_names(self):
        async with self.async_engine.connect() as conn:
            tables = await conn.run_sync(
                lambda sync_conn: sql.inspect(sync_conn).get_table_name()
            )
            return tables


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = SessionManager().get_session()

    async with async_session:
        try:
            yield async_session
            await async_session.commit()
        except SQLAlchemyError as exc:
            await async_session.rollback()
            raise exc
        finally:
            await async_session.close()
