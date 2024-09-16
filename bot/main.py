import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.header.start import router as router_start

router = Router()
router.include_router(router_start)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot, skip_updates=True)
    except asyncio.CancelledError:
        logging.info("Polling stopped.")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
