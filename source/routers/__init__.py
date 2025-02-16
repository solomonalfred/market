from .admin import router as ad_router
from .auth import router as a_router
from .user import router as u_router

__all__ = (a_router, u_router, ad_router)
