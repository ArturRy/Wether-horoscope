import os
from datetime import datetime

from aiogram import types, Bot

from math import ceil

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from sqlalchemy import select, func, update

from data_base.models import Session, User
from forms.forms import Admin
from keyboards.reply import admin_keyboard

load_dotenv()

ADMIN_IDS = os.getenv("ADMIN_IDS").split(",")
print(ADMIN_IDS)


async def get_admin_panel(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id in ADMIN_IDS:
        await message.answer("Вот и панелька", reply_markup=admin_keyboard())
        await state.clear()


async def delete_user(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user_id in ADMIN_IDS:
        await message.answer("Введите ID пользователя, которого хотите удалить")
        await state.set_state(Admin.DELETE_USER)


async def get_delete_user_id(message: Message, state: FSMContext):
    async with Session() as session:
        try:
            user_id = int(message.text)
            user = await session.scalar(select(User).where(User.tg_user_id == user_id))
            await session.delete(user)
            await session.commit()
            await message.answer(f"Пользователь с ID {message.text} удален")
            await state.clear()

        except:
            await message.answer(f"Пользователя с ID {message.text} не существует")
            await state.clear()


async def redact_user_params(message: Message, state: FSMContext):
    await message.answer(
        "Введите ID пользователя, а также необходимые параметры через запятую для редактирования "
        "параметров\n"
        "user_name - Имя пользователя\n"
        "zodiac - Знак зодиака формат(libra_Весы_♎)\n"
        "city - Город\n"
        "reminder - Время ежедневных сообщений, формат(HH:MM)\n"
        "status - Булевое поле True=Любое знаечение, False=пустое значение\n"
        "premium - Datetime field формат(2024-07-07 11:07:08.615)"
    )
    await state.set_state(Admin.SET_PARAMS)


async def set_new_params(message: Message, state: FSMContext):
    async with Session() as session:
        try:
            user_id = int(message.text.split(",")[0])
            user_params = message.text.split(",")[1::]
            kwargs = {}
            for param in user_params:
                par = param.strip().split("=")
                if par[0] == "status":
                    par_dict = {par[0]: bool(par[1])}
                elif par[0] == "premium":

                    par_dict = {
                        par[0]: datetime.strptime(par[1], "%Y-%m-%d %H:%M:%S.%f")
                    }

                else:
                    par_dict = {par[0]: par[1]}
                kwargs.update(par_dict)
            q = update(User).where(User.tg_user_id == user_id).values(**kwargs)
            await session.execute(q)
            await session.commit()
            await state.clear()
            await message.answer("Параметры успешно изменены")

        except:
            await message.answer("Указаны неверные параметры пользователя")


async def get_records_page(page: int, page_size: int):
    async with Session() as session:
        query = select(User).limit(page_size).offset((page - 1) * page_size)
        result = await session.execute(query)
    return [
        {column: getattr(row, column) for column in row.__table__.columns.keys()}
        for row in result.scalars().all()
    ]


async def get_total_pages(page_size: int):
    async with Session() as session:
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        total_records = result.scalar_one()
        return ceil(total_records / page_size)


PAGE_SIZE = 3


async def get_page_keyboard(current_page: int, total_pages: int):
    keyboard = InlineKeyboardBuilder()

    if current_page > 1:
        keyboard.add(
            InlineKeyboardButton(text="⏪", callback_data=f"page:{current_page - 1}")
        )

    keyboard.add(
        types.InlineKeyboardButton(
            text=f"{current_page} / {total_pages}", callback_data="current_page"
        )
    )

    if current_page < total_pages:
        keyboard.add(
            types.InlineKeyboardButton(
                text="⏩", callback_data=f"page:{current_page + 1}"
            )
        )

    # Если нет других кнопок, добавляем кнопку по умолчанию
    if not keyboard.buttons:
        keyboard.add(
            types.InlineKeyboardButton(tetx="No pages", callback_data="no_pages")
        )

    return keyboard.as_markup()


async def start_cmd_handler(message: types.Message, bot: Bot):
    user_id = str(message.from_user.id)
    if user_id in ADMIN_IDS:
        page = 1
        total_pages = await get_total_pages(PAGE_SIZE)
        records_page = await get_records_page(page, PAGE_SIZE)
        keyboard = await get_page_keyboard(page, total_pages)

        await bot.send_message(
            message.chat.id, format_records(records_page), reply_markup=keyboard
        )
    else:
        await message.answer("Вы не являетесь админом ⛔️")


async def process_callback_page_button(callback_query: types.CallbackQuery, bot: Bot):
    page = int(callback_query.data.split(":")[1])
    total_pages = await get_total_pages(PAGE_SIZE)
    records_page = await get_records_page(page, PAGE_SIZE)
    keyboard = await get_page_keyboard(page, total_pages)

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=format_records(records_page),
        reply_markup=keyboard,
    )
    await bot.answer_callback_query(callback_query.id)


def format_records(records):
    return "".join(
        [
            f"➖➖➖➖➖\n"
            f'ID - {user["tg_user_id"]}\n'
            f'Имя - {user["user_name"]}\n'
            f'Город - {user["city"]}\n'
            f'Премиум - {user["premium"]}\n'
            f'Статус - {user["status"]}\n'
            for user in records
        ]
    )
