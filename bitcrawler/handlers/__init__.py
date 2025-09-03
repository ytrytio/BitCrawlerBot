from .messages import router as msg_router
from .callbacks import router as cb_router

routers = [msg_router, cb_router]

__all__ = ["routers"]
