import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv

from app.admin import (
    get_admin_panel,
    delete_user,
    get_delete_user_id,
    redact_user_params,
    set_new_params,
    start_cmd_handler,
    process_callback_page_button,
)
from app.handlers import (
    by_premium,
    start,
    change_city,
    get_new_city,
    change_zodiac,
    get_new_zodiac,
    set_reminder_time,
    get_reminder_time,
    get_user_info,
    set_status,
    get_status,
    take_a_gift,
    user_help,
)
from app.pay import day_sub, month_sub, year_sub, pre_checkout_query, successful_payment
from commands.commands import set_commands
from data_base.models import init_db
from forms.forms import HoroscopeForm, UserRegForm, Weather, TimeForm, Admin
from middlewaries.tg_sheduler import every_day
from register.user_reg import (
    user_registration,
    get_user_name,
    get_user_zodiac,
    get_user_city,
    paste_to_db,
)

from weather.handlers import choose_city, get_weather
from horoscope.horoscope import choose_zodiac, get_horoscope

load_dotenv()
TOKEN = os.getenv("BOT_ID")

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")


async def main():
    await init_db()
    dp = Dispatcher()
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await every_day(bot)
    await set_commands(bot)

    # Admin pannel
    dp.message.register(get_admin_panel, Command(commands=["admin"]))
    dp.message.register(delete_user, F.text == "Удалить пользователя")
    dp.message.register(get_delete_user_id, Admin.DELETE_USER)
    dp.message.register(redact_user_params, F.text == "Изменить данные пользователя")
    dp.message.register(set_new_params, Admin.SET_PARAMS)

    dp.message.register(start_cmd_handler, F.text == "Список пользователей")
    dp.callback_query.register(process_callback_page_button, F.data.startswith("page:"))

    dp.message.register(by_premium, F.text == "Купить подписку 👛")
    dp.callback_query.register(year_sub, F.data == "year")
    dp.callback_query.register(month_sub, F.data == "month")
    dp.callback_query.register(day_sub, F.data == "days")
    dp.message.register(take_a_gift, F.text == "Получить ПОДАРОЧЕК 🎁")

    dp.pre_checkout_query.register(pre_checkout_query)
    dp.message.register(successful_payment, F.content_type == "successful_payment")

    dp.message.register(start, Command(commands=["start"]))
    dp.message.register(user_help, Command(commands=["help"]))
    dp.message.register(choose_zodiac, Command(commands=["horoscope"]))
    dp.message.register(choose_city, Command(commands=["weather"]))
    dp.message.register(get_weather, Weather.GET_CITY)
    dp.callback_query.register(get_horoscope, HoroscopeForm.GET_HORO)
    dp.message.register(user_registration, Command(commands=["registration"]))
    dp.message.register(get_user_name, UserRegForm.GET_NAME)
    dp.callback_query.register(get_user_zodiac, UserRegForm.GET_ZODIAC)
    dp.message.register(get_user_city, UserRegForm.GET_CITY)
    dp.callback_query.register(paste_to_db, UserRegForm.REGISTER)

    dp.message.register(change_city, F.text == "Изменить город 🌃")
    dp.message.register(get_new_city, Weather.NEW_CITY)

    dp.message.register(change_zodiac, F.text == "Изменить знак зодиака ♎️")
    dp.callback_query.register(get_new_zodiac, HoroscopeForm.NEW_ZODIAC)

    dp.message.register(set_reminder_time, F.text == "Установить время ⏳")
    dp.message.register(get_reminder_time, TimeForm.SET_TIME)
    dp.message.register(
        set_status, F.text == "Включить/Выключить\n" "ежедневный прогноз 🕹"
    )
    dp.callback_query.register(get_status, TimeForm.SET_STATUS)

    dp.message.register(get_user_info, F.text == "Получить информацию об аккаунте 🗒")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
