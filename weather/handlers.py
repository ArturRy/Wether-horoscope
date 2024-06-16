import json
import datetime
import os
from dotenv import load_dotenv
import requests
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from forms.forms import Weather

load_dotenv()
API = os.getenv("WEATHER_API")

descriptions = {
    "Clear": "Ясно \U00002600",
    "Clouds": "Облачно \U00002601",
    "Rain": "Дождь \U00002614",
    "Drizzle": "Дождь \U00002614",
    "Thunderstorm": "Гроза \U000026A1",
    "Snow": "Снег \U0001F328",
    "Mist": "Туман \U0001F32B",
}


async def choose_city(message: Message, state: FSMContext):
    await message.answer("Укажите ваш город")
    await state.set_state(Weather.GET_CITY)


async def get_weather(message: Message, state: FSMContext):
    city = message.text.title()
    request = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&units=metric&appid={API}"
    )
    try:
        data = json.loads(request.text)
        print(f"{message.from_user.first_name} \n {message.from_user.id}")
        temperature = data["main"]["temp"]
        description = data["weather"][0]["main"]
        if description in descriptions:
            descr = descriptions[description]
        else:
            descr = "Атмосферу сдуло в космос: 🪙"
        sunrise_timestamp = datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"]
        ).strftime("%H:%M")
        sunset_timestamp = datetime.datetime.fromtimestamp(
            data["sys"]["sunset"]
        ).strftime("%H:%M")
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        answer = (
            f"Сегодня: {date} 🗓\n"
            f"В городе {city} сейчас {temperature} °C 🌡\n"
            f"{descr}\n"
            f"Восход: {sunrise_timestamp} 🌅\n"
            f"Закат: {sunset_timestamp} 🌆\n"
            f"Ветер: {wind} метров в секунду 🌬\n"
            f"Давление: {pressure} мм.рт.ст. 🧪\n"
            f"Влажность: {humidity} % 💧"
        )
        await state.clear()
        await message.answer(answer)
    except:
        await message.answer("Таких городов мы не знаем, попробуйте снова")
