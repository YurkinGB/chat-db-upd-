from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *

api = '7'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

initiate_db()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Регистрация')],
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация'),
            KeyboardButton(text='Купить')
        ]
    ], resize_keyboard=True
)

inline_kb = InlineKeyboardMarkup()
inline_calc_bt = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
inline_formulas_bt = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_kb.add(inline_calc_bt)
inline_kb.add(inline_formulas_bt)

by_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Товар1', callback_data='product_buying')],
        [InlineKeyboardButton(text='Товар2', callback_data='product_buying')],
        [InlineKeyboardButton(text='Товар3', callback_data='product_buying')],
        [InlineKeyboardButton(text='Товар4', callback_data='product_buying')],
    ]
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


#_______________________________Функции цепочки состояний RegistrationState_____________________________________________
@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer(f'Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await message.answer(f'Пользователь существует, введите другое имя')
        await RegistrationState.username.set()
    else:
        await state.update_data(username=message.text)
        await message.answer(f'Введите свой email:')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer(f'Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await state.finish()
    await message.answer(f'Регистрация прошла успешно')

#__________________________________________Покупка продукта_____________________________________________________________
@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for product in get_all_products():
        await message.answer(f'Название: Product {product[1]} | Описание: описание {product[2]} '
                             f'| Цена: {product[3]}руб>')
        with open(f'foto/bad{product[0]}.jpg', 'rb') as photo:
            await message.answer_photo(photo)
    await message.answer(f'Выберите продукт:', reply_markup=by_kb)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer(f'Вы успешно приобрели продукт!')
    await call.answer()


#______________________Расчет калорий и Функции цепочки состояний UserState(StatesGroup)_______________________________
@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer(f'Выберите опцию', reply_markup=inline_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer(f'"для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;\n '
                              f'для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161"')
    await call.answer()


@dp.message_handler(commands=['Start'])
async def chat_start(message):
    await message.answer(f'Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer(f'Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = 10 * int(data['growth']) + 6.25 * int(data['weight']) - 5 * int(data['age']) - 161
    await message.answer(f'Ваша норма калорий {calories}')
    await state.finish()


@dp.message_handler()
async def all_message(message):
    await message.answer(f'чтобы продолжить выберите команду "Рассчитать"', reply_markup=kb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    connection.close()
