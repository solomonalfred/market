from .auth import credentials_exception
from .auth import router as a_router
from .user import router as u_router
from .admin import router as ad_router
__all__ = (a_router, u_router, ad_router)
