from aiogram import Bot, Dispatcher
from pydantic_settings import BaseSettings
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_USER: str
    DB_PASS: str
    DB_NAME: str


settings = Settings()

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
