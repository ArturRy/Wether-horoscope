import re
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select

from data_base.models import Session, User
from forms.forms import HoroscopeForm, Weather, TimeForm
from keyboards.inline import by_premium_keyboard, get_zodiac_keyboard, on_off_keyboard
from keyboards.reply import get_reply_keyboard, get_reply_keyboard_gift

from middlewaries.tg_sheduler import send_message_cron


async def start(message: Message, state: FSMContext):
    async with Session() as session:
        await state.clear()
        user = await session.scalar(
            select(User).where(User.tg_user_id == message.from_user.id)
        )
        if user:
            if user.gift:
                name = user.user_name
                await message.answer(
                    f"Привет {name}, чем займемся сегодня?",
                    reply_markup=get_reply_keyboard_gift(),
                )
            else:
                name = user.user_name
                await message.answer(
                    f"Привет {name}, чем займемся сегодня?",
                    reply_markup=get_reply_keyboard(),
                )

        else:
            await message.answer(
                "Привет, я бот погоды и предсказаний\n"
                "Я могу показать погоду в любом городе\n"
                "Или рассказать, о чем Вам пророчат звезды\n"
                "Просто воспользуйтесь командами \n/weather и /horoscope\n"
                "Для получения расширенных возможностей пройдите регистрацию \n/registration\n"
                "Чтобы получить более подробную информацию, используйте  команду \n/help"
            )


async def by_premium(message: Message):
    await message.answer(
        "Выберите подходящий тариф\n"
        "Сервис оплаты тестовый и \nНЕ ИСПОЛЬЗУЕТ РЕАЛЬНЫЕ ДЕНЬГИ\n"
        "Для приобретения подписки введите следующие данные карты:\n"
        "1111 1111 1111 1026\n"
        "12/22   000",
        reply_markup=by_premium_keyboard(),
    )


async def change_city(message: Message, state: FSMContext):
    await message.answer("Введите новый город")
    await state.set_state(Weather.NEW_CITY)


async def get_new_city(message: Message, state: FSMContext):
    async with Session() as session:
        tg_id = message.from_user.id
        user = await session.scalar(select(User).where(User.tg_user_id == tg_id))
        user.city = message.text
        await session.commit()
        await state.clear()
        await message.answer(f"Ваш город успешно изменен на {message.text}")


async def change_zodiac(message: Message, state: FSMContext):
    await message.answer(
        "Выберите новый знак зодиака", reply_markup=get_zodiac_keyboard()
    )
    await state.set_state(HoroscopeForm.NEW_ZODIAC)


async def get_new_zodiac(call: CallbackQuery, state: FSMContext):
    async with Session() as session:
        user = await session.scalar(
            select(User).where(User.tg_user_id == call.from_user.id)
        )
        zodiac = call.data
        user.zodiac = zodiac
        await session.commit()
        await call.message.answer(
            f'Ваш знак успешно изменен на {",".join(zodiac.split("_")[1::]).replace(",", " ")}'
        )
        await state.clear()


async def set_reminder_time(message: Message, state: FSMContext):
    async with Session() as session:
        user: User = await session.scalar(
            select(User).where(User.tg_user_id == message.from_user.id)
        )
        if not user.premium:
            await message.answer(
                "Для возможности установить время ежедневных прогнозов необходимо приобрести "
                "подписку"
            )
            return
        await message.answer(
            "Введите желаемое время рассылки погоды и гороскопа \n"
            "в формате HH:MM, например 18:30"
        )
        await state.set_state(TimeForm.SET_TIME)


async def get_reminder_time(message: Message, state: FSMContext, bot: Bot):
    async with Session() as session:
        from main import scheduler

        time = re.compile(r"(^[0-2])?([0-9]) ?(.)? ?([0-5])(W*[0-9])")

        check_set = re.findall(time, message.text)
        if check_set:
            set_time = re.sub(time, r"\1\2:\4\5", message.text)

            user: User = await session.scalar(
                select(User).where(User.tg_user_id == message.from_user.id)
            )
            user.reminder = set_time
            user.status = True
            await session.commit()
            await message.answer(f"Время ежедневных прогнозов изменено на {set_time}")
            await state.clear()

            if not user.premium:
                pass
            if user.premium > datetime.now():
                hour = set_time.split(":")[0]
                minute = set_time.split(":")[1]
                scheduler.add_job(
                    send_message_cron,
                    id=str(message.from_user.id),
                    trigger="cron",
                    hour=hour,
                    minute=minute,
                    start_date=datetime.now(),
                    replace_existing=True,
                    kwargs={
                        "bot": bot,
                        "user_id": user.tg_user_id,
                        "user_zodiac": user.zodiac,
                        "user_city": user.city,
                    },
                )
            else:
                user.status = False
                await session.commit()
                await message.answer("Премиум подписка истекла 😳")

                scheduler.print_jobs()
        else:
            await message.answer("Неверный формат ввода, пожалуйста попробуйте еще раз")


async def get_user_info(message: Message):
    async with Session() as session:
        user: User = await session.scalar(
            select(User).where(User.tg_user_id == message.from_user.id)
        )
        zodiac = ",".join(user.zodiac.split("_")[1::]).replace(",", " ")
        if user.status:
            status = "🟢"
        else:
            status = "🔴"

        try:
            prem_days = int(str((user.premium - datetime.now())).split(" ")[0])
            if prem_days > 0:
                pass
            else:
                prem_days = "Премиум подписка истекла"

        except:
            prem_days = "Вы не приобрели премиум подписку 🏦"

        user_info = (
            f"Имя: {user.user_name}\n"
            f"Город:  {user.city}\n"
            f"Знак зодиака:  {zodiac}\n"
            f"Время ежедневных сообщений:  {user.reminder}\n"
            f"Статус ежедневных сообщений: {status}\n"
            f"Осталось дней премиум подписки: {prem_days}"
        )

        await message.answer(user_info)


async def set_status(message: Message, state: FSMContext):
    async with Session() as session:
        user: User = await session.scalar(
            select(User).where(User.tg_user_id == message.from_user.id)
        )
        if not user.premium:
            await message.answer(
                "Для возможности установить статус ежедневных прогнозов необходимо приобрести"
                "подписку"
            )
            return
        await message.answer(
            "Выберите статус ежедневного прогноза", reply_markup=on_off_keyboard()
        )
        await state.set_state(TimeForm.SET_STATUS)


async def get_status(call: CallbackQuery, state: FSMContext):
    async with Session() as session:
        from main import scheduler

        user: User = await session.scalar(
            select(User).where(User.tg_user_id == call.from_user.id)
        )
        status = call.data
        if status == "Активен 🟢":

            scheduler.resume_job(job_id=str(call.from_user.id))
            user.status = True

        else:

            scheduler.pause_job(job_id=str(call.from_user.id))
            user.status = False

        await session.commit()
        await call.message.answer(f"Статус ежедневных оповещений: {status}")
        await state.clear()


async def take_a_gift(message: Message):
    async with Session() as session:
        user: User = await session.scalar(
            select(User).where(User.tg_user_id == message.from_user.id)
        )
        if user.gift:
            if not user.premium:
                user.premium = datetime.now() + timedelta(days=30)
                user.gift = False
                await session.commit()
            else:
                if user.premium >= datetime.now():
                    user.premium = user.premium + timedelta(days=30)
                    user.gift = False
                    await session.commit()
                elif user.premium < datetime.now():
                    user.premium = datetime.now() + timedelta(days=30)
                    user.gift = False
                    await session.commit()
            await message.answer(
                "Вам начислено 30 дней премиум подписки 🤩",
                reply_markup=get_reply_keyboard(),
            )
            await message.delete()


async def user_help(message: Message):
    await message.answer(
        "Этот бот может работать без регистраций и подписки, вам сразу доступны такие функции, "
        "как посмотреть погоду на данный момент времени в указанном городе, и гороскоп на сегодня."
        "Достаточно воспользоваться командами /weather и /horoscope соответственно."
        "Эти команды доступны по кнопке меню внизу слева, либо можно ввести их вручную\n\n"
        "Для получения расширенных опций необходимо пройти регистрацию и приобрести премиум подписку."
        "Вам станет доступна функция установить ежедневный прогноз погоды и гороскопа в указанное "
        "время\n\n"
        "Чтобы оставить сообщение о неисправностях или ошибках в работе бота напишите в канал бота"
        " https://t.me/+Xe7A91ZRYcFlZGEy. Здесь также можно оставить отзывы или пожелания по работе "
        "и функционалу бота"
    )
