from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select
from source.utils.build_engine import get_async_session, User
from source.config import get_settings
from source.constants import APIINFO
from source.routers import __all__ as routers
from source.utils.hasher import PasswordManager


hasher = PasswordManager()

@asynccontextmanager
async def get_db_session_cm():
    async for session in get_async_session():
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    async with get_db_session_cm() as db:
        result = await db.execute(select(User).where(User.login == settings.ADMIN_LOGIN))
        user = result.scalars().one_or_none()
        if user is None:
            new_user = User(
                login=settings.ADMIN_LOGIN,
                password_hash=hasher.hash_password(settings.ADMIN_PASSWORD.get_secret_value()),
                email=settings.ADMIN_EMAIL,
                first_name=settings.ADMIN_LOGIN,
                last_name=settings.ADMIN_LOGIN,
                role="admin"
            )
            new_user.coin_amount = 1_000_000
            db.add(new_user)
            await db.commit()
    yield

def get_application():
    app = FastAPI(
        lifespan=lifespan,
        title=APIINFO.title,
        version=APIINFO.version
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in routers:
        app.include_router(router)

    # await build()

    return app

app = get_application()
