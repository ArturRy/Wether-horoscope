import json
from datetime import datetime, timedelta

import requests
from aiogram import Bot
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from data_base.models import Session, User
from horoscope.horoscope import get_text_horoscope
from keyboards.reply import get_reply_keyboard

from weather.handlers import get_weather, descriptions, API


async def send_message_cron(bot: Bot, user_id: int, user_zodiac, user_city):
    city = user_city

    request = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid={API}"
    )

    try:
        data = json.loads(request.text)

        temperature = data["main"]["temp"]
        description = data["weather"][0]["main"]

        if description in descriptions:
            descr = descriptions[description]
        else:
            descr = "Атмосферу сдуло в космос: 🪙"
        sunrise_timestamp = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime(
            "%H:%M"
        )
        sunset_timestamp = datetime.fromtimestamp(data["sys"]["sunset"]).strftime(
            "%H:%M"
        )
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        weather_text = (
            f"Сегодня: {date} 🗓\n"
            f"В городе {city} сейчас {temperature} °C 🌡\n"
            f"{descr}\n"
            f"Восход: {sunrise_timestamp} 🌅\n"
            f"Закат: {sunset_timestamp} 🌆\n"
            f"Ветер: {wind} метров в секунду 🌬\n"
            f"Давление: {pressure} мм.рт.ст. 🧪\n"
            f"Влажность: {humidity} % 💧\n"
        )

        zodiac = user_zodiac.split("_")[0]
        us_zodiac = ",".join(user_zodiac.split("_")[1::]).replace(",", " ")
        horoscope_text = await get_text_horoscope(zodiac, user_zodiac=us_zodiac)

        answer = weather_text + horoscope_text
        await bot.send_message(user_id, answer)

    except:
        await bot.send_message(user_id, "Таких городов мы не знаем, попробуйте снова")


async def every_day(bot: Bot):
    async with Session() as session:

        users = await session.scalars(select(User))
        from main import scheduler

        for user in users:

            if user.status:
                try:

                    time: str = user.reminder

                    if time:
                        hour = time.split(":")[0]
                        minute = time.split(":")[1]
                        if not user.premium:
                            continue
                        if user.premium > datetime.now():
                            scheduler.add_job(
                                send_message_cron,
                                id=str(user.tg_user_id),
                                trigger="cron",
                                hour=hour,
                                minute=minute,
                                start_date=datetime.now(),
                                kwargs={
                                    "bot": bot,
                                    "user_id": user.tg_user_id,
                                    "user_zodiac": user.zodiac,
                                    "user_city": user.city,
                                },
                            )

                        else:
                            await bot.send_message(
                                user.tg_user_id, "Ваша преимум подписка истекла 😳"
                            )
                            user.status = False
                            await session.commit()

                finally:
                    print(scheduler.print_jobs())
        scheduler.start()


# print((datetime.now() + timedelta(days=30)) )
# print(datetime.now())
