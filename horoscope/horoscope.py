import httpx
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bs4 import BeautifulSoup

from forms.forms import HoroscopeForm
from keyboards.inline import get_zodiac_keyboard

headers = {
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


async def get_response(link: str):
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as htx:
        result: httpx.Response = await htx.get(url=link)
        if result.status_code != 200:
            return await get_response(link=link)
        else:
            return await result.aread()


async def get_text_horoscope(zodiac: str, user_zodiac: str):
    link = f"https://horo.mail.ru/prediction/{zodiac}/today/"
    response_result = await get_response(link=link)
    beautifulsoup: BeautifulSoup = BeautifulSoup(
        markup=response_result, features="lxml"
    )
    text = beautifulsoup.find(
        name="div",
        class_="article__item article__item_alignment_left article__item_html",
    )
    graphic_str = "♈️♉️♊️♋️♌️♍️♎️♏️♐️♑️♒️♓️♈️♉️♊️♋️♌️\n"
    return graphic_str + user_zodiac + "\n" + text.text


async def choose_zodiac(message: Message, bot: Bot, state: FSMContext):
    print(f"{message.from_user.first_name} \n {message.from_user.id}")
    await bot.send_message(
        message.chat.id, "Выберите знак зодика", reply_markup=get_zodiac_keyboard()
    )
    await state.set_state(HoroscopeForm.GET_HORO)


async def get_horoscope(call: CallbackQuery, state: FSMContext):

    await call.answer()
    zodiac = call.data.split("_")[0]
    user_zodiac = " ".join(call.data.split("_")[1::])
    print(call.data)

    text = await get_text_horoscope(zodiac=zodiac, user_zodiac=user_zodiac)
    await call.message.edit_text(text=text)
    await state.clear()
