from .callbacks import setup_callbacks_router
from .messages import setup_messages_router

def get_routers(name: str):
    return [
        setup_callbacks_router(name),
        setup_messages_router(name),
    ]

__all__ = ["get_routers"]
