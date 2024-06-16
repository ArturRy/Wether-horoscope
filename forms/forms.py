from aiogram.fsm.state import StatesGroup, State


class UserRegForm(StatesGroup):
    GET_ZODIAC = State()
    GET_NAME = State()
    REGISTER = State()
    GET_CITY = State()
    CHANGE_CITY = State()


class Weather(StatesGroup):
    GET_CITY = State()
    NEW_CITY = State()


class HoroscopeForm(StatesGroup):
    GET_HORO = State()
    NEW_ZODIAC = State()


class TimeForm(StatesGroup):
    SET_TIME = State()
    SET_STATUS = State()


class Admin(StatesGroup):
    DELETE_USER = State()
    SET_PARAMS = State()
