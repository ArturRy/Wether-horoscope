import datetime
import os

from aiogram import Bot
from aiogram.types import PreCheckoutQuery, Message, LabeledPrice, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select

from data_base.models import Session, User
from dotenv import load_dotenv

load_dotenv()

PAYMENT_ID = os.getenv("PAYMENT_ID")


def keyboards():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Оплатить заказ", pay=True)
    # keyboard.button(text='Link', url='https://animego.org/')
    keyboard.adjust(1)
    return keyboard.as_markup()


async def year_sub(call: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=call.message.chat.id,
        title="Подписка на 365 дней",
        description="Оплата подписки",
        payload="year",
        provider_token=f"{PAYMENT_ID}",
        currency="rub",
        prices=[LabeledPrice(label="Подписка на гороскоп и погоду", amount=500 * 100)],
        max_tip_amount=5000,
        suggested_tip_amounts=[1000, 2000, 3000, 5000],
        start_parameter="nztcoder",
        provider_data=None,
        # photo_url='https://animego.org/media/cache/thumbs_250x350/upload/anime/images/65f5518028128803053465.jpg',
        photo_url="https://github.com/ArturRy/Skraping_DZ/blob/main/prem_1.jpg?raw=true",
        photo_size=100,
        photo_width=800,
        photo_height=450,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=keyboards(),
        request_timeout=15,
    )


async def month_sub(call: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=call.message.chat.id,
        title="Подписка на 30 дней",
        description="Оплата подписки",
        payload="month",
        provider_token=f"{PAYMENT_ID}",
        currency="rub",
        prices=[LabeledPrice(label="Подписка на гороскоп и погоду", amount=150 * 100)],
        max_tip_amount=5000,
        suggested_tip_amounts=[1000, 2000, 3000, 5000],
        start_parameter="nztcoder",
        provider_data=None,
        photo_url="https://github.com/ArturRy/Skraping_DZ/blob/main/prem_2.png?raw=true",
        photo_size=100,
        photo_width=800,
        photo_height=450,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=keyboards(),
        request_timeout=15,
    )


async def day_sub(call: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=call.message.chat.id,
        title="Подписка на 10 дней",
        description="Оплата подписки",
        payload="days",
        provider_token=f"{PAYMENT_ID}",
        currency="rub",
        prices=[LabeledPrice(label="Подписка на гороскоп и погоду", amount=100 * 100)],
        max_tip_amount=5000,
        suggested_tip_amounts=[1000, 2000, 3000, 5000],
        start_parameter="nztcoder",
        provider_data=None,
        photo_url="https://github.com/ArturRy/Skraping_DZ/blob/main/prem_3.jpg?raw=true",
        photo_size=100,
        photo_width=800,
        photo_height=450,
        need_name=False,
        need_phone_number=False,
        need_email=False,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=False,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=keyboards(),
        request_timeout=15,
    )


async def pre_checkout_query(pre_check_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_check_query.id, ok=True)


async def successful_payment(message: Message):
    async with Session() as session:
        user: User = await session.scalar(
            select(User).where(User.tg_user_id == message.from_user.id)
        )
        premium_pay = message.successful_payment.invoice_payload
        if premium_pay == "days":
            premium_days = 10
        elif premium_pay == "month":
            premium_days = 30
        elif premium_pay == "year":
            premium_days = 365
        if not user.premium:
            user.premium = datetime.datetime.now() + datetime.timedelta(
                days=premium_days
            )
            await session.commit()
        else:
            if user.premium >= datetime.datetime.now():
                user.premium = user.premium + datetime.timedelta(days=premium_days)
                await session.commit()
            elif user.premium < datetime.datetime.now():
                user.premium = datetime.datetime.now() + datetime.timedelta(
                    days=premium_days
                )
                await session.commit()
        user_prem_days = int(
            str((user.premium - datetime.datetime.now())).split(" ")[0]
        )
        msg = (
            f"Спасибо за оплату {message.successful_payment.total_amount // 100}{message.successful_payment.currency}."
            f" \r\nДней премиум подписки осталось: {user_prem_days}"
        )
        await message.answer(msg)
