from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from data_base.models import Session, User
from keyboards.inline import get_zodiac_keyboard, yes_or_no
from forms.forms import UserRegForm
from keyboards.reply import get_reply_keyboard, get_reply_keyboard_gift

channel = "-1002206989771"


async def user_registration(message: Message, bot: Bot, state: FSMContext):
    async with Session() as session:
        tg_id = message.from_user.id
        user = await session.scalar(select(User).where(User.tg_user_id == tg_id))
        # chat_member = await bot.get_chat_member(chat_id=channel, user_id=tg_id)
        if user:
            await message.answer(
                "Вы уже зарегистрированы", reply_markup=get_reply_keyboard()
            )
            await state.set_state(UserRegForm.CHANGE_CITY)
        else:
            # elif chat_member.status == 'member':
            await message.answer("Введите ваше имя")
            await state.set_state(UserRegForm.GET_NAME)
            # await message.answer('Только пользователи с подпиской на канал могут пройти регистрацию\n'
            #                      'Для регистрации пройдите по ссылке: https://t.me/+Xe7A91ZRYcFlZGEy')


async def get_user_name(message: Message, state: FSMContext):
    await message.answer("Выберите знак зодиака", reply_markup=get_zodiac_keyboard())
    await state.update_data(user_name=message.text)
    await state.set_state(UserRegForm.GET_ZODIAC)


async def get_user_zodiac(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Напишите свой город")

    await state.update_data(zodiac=call.data)
    await state.set_state(UserRegForm.GET_CITY)


async def get_user_city(message: Message, state: FSMContext):
    await state.update_data(tg_user_id=message.from_user.id, city=message.text)
    data = await state.get_data()
    await message.answer(
        f"Проверьте данные, все указано верно?\n"
        f'Ваше имя: {data.get("user_name")}\n'
        f'Ваш город: {data.get("city")}\n'
        f'Ваш знак зодиака: {data.get("zodiac").split("_")[1]}\n'
        f"      🧐  ",
        reply_markup=yes_or_no(),
    )

    await state.set_state(UserRegForm.REGISTER)


async def paste_to_db(call: CallbackQuery, state: FSMContext):
    answer = call.data
    if answer == "yes":
        async with Session() as session:

            data = await state.get_data()
            user_info = User(
                tg_user_id=data.get("tg_user_id"),
                user_name=data.get("user_name"),
                city=data.get("city"),
                zodiac=data.get("zodiac"),
            )
            session.add(user_info)
            await session.commit()
            await state.clear()
            await call.message.answer(
                "Вы успешно зарегистрированы 😎", reply_markup=get_reply_keyboard_gift()
            )

    else:
        await call.message.answer(
            "Выберите команду /register и начните опрос сначала\r\n"
            "Или продолжайте пользоваться ботом без регистрации"
        )
        await state.clear()
        return
