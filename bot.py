from aiogram.utils import executor
from aiogram import Dispatcher

from handlers import register_all_handlers
from loader import dp


async def start_up(dp: Dispatcher) -> None:
    register_all_handlers(dp)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=False,
        on_shutdown=shutdown,
        on_startup=start_up,
    )
