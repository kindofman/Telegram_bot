from aiogram import Dispatcher

from handlers.admin import register_admin_handlers
from handlers.user import register_user_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_admin_handlers,
        register_user_handlers,
    )
    for handler in handlers:
        handler(dp)