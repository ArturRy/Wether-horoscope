from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_reply_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()

    keyboard_builder.button(text="Купить подписку 👛")
    keyboard_builder.button(text="Установить время ⏳")

    keyboard_builder.button(text="Изменить город 🌃")
    keyboard_builder.button(text="Изменить знак зодиака ♎️")
    keyboard_builder.button(text="Получить информацию об аккаунте 🗒")
    keyboard_builder.button(text="Включить/Выключить\n" "ежедневный прогноз 🕹")
    keyboard_builder.adjust(2, 2, 1, 1)
    return keyboard_builder.as_markup(resize_keyboard=True)


def get_reply_keyboard_gift():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Получить ПОДАРОЧЕК 🎁")
    keyboard_builder.button(text="Купить подписку 👛")
    keyboard_builder.button(text="Установить время ⏳")

    keyboard_builder.button(text="Изменить город 🌃")
    keyboard_builder.button(text="Изменить знак зодиака ♎️")
    keyboard_builder.button(text="Получить информацию об аккаунте 🗒")

    keyboard_builder.button(text="Включить/Выключить\n" "ежедневный прогноз 🕹")

    keyboard_builder.adjust(
        1,
        2,
        2,
        1,
        1,
    )
    return keyboard_builder.as_markup(resize_keyboard=True)


def admin_keyboard():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text="Список пользователей")
    keyboard_builder.button(text="Удалить пользователя")
    keyboard_builder.button(text="Изменить данные пользователя")
    keyboard_builder.adjust(1, 1, 1)
    return keyboard_builder.as_markup(resize_keyboard=True)
