from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_zodiac_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text=f"Овен \U00002648", callback_data="aries_Овен_♈")
    keyboard_builder.button(text="Телец \U00002649", callback_data="taurus_Телец_♉")
    keyboard_builder.button(
        text="Близнецы \U0000264A", callback_data="gemini_Близнецы_♊"
    )
    keyboard_builder.button(text="Рак \U0000264B", callback_data="cancer_Рак_️️️♋")
    keyboard_builder.button(text="Лев \U0000264C", callback_data="leo_Лев_♌")
    keyboard_builder.button(text="Дева \U0000264D", callback_data="virgo_Дева_♍")
    keyboard_builder.button(text="Весы \U0000264E", callback_data="libra_Весы_♎")
    keyboard_builder.button(
        text="Скорпион \U0000264F", callback_data="scorpio_Скорпион_♏"
    )
    keyboard_builder.button(
        text="Стрелец \U00002650", callback_data="sagittarius_Стрелец_️️️️♐"
    )
    keyboard_builder.button(
        text="Козерог \U00002651", callback_data="capricorn_Козерог_♑️"
    )
    keyboard_builder.button(
        text="Водолей \U00002652", callback_data="aquarius_Водолей_♒"
    )
    keyboard_builder.button(text="Рыбы \U00002653", callback_data="pisces_Рыбы_♓")
    keyboard_builder.adjust(3)

    return keyboard_builder.as_markup()


def yes_or_no():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Да ✅", callback_data="yes")
    keyboard_builder.button(text="Нет ❌", callback_data="no")
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()


def by_premium_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="Подписка на год\n" "    500 rub 💰💰💰", callback_data="year"
    )
    keyboard_builder.button(
        text="Подписка на месяц\n" "    150 rub 💰💰", callback_data="month"
    )
    keyboard_builder.button(
        text="Подписка на 10 дней\n" "      100 rub 💰", callback_data="days"
    )
    keyboard_builder.adjust(1, 1, 1)
    return keyboard_builder.as_markup()


def on_off_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Активировать 🟢", callback_data="Активен 🟢")
    keyboard_builder.button(text="Отключить 🔴", callback_data="Не активен 🔴")
    keyboard_builder.adjust(2)
    return keyboard_builder.as_markup()
