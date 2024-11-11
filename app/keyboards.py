from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from app.database.requests import get_available_habits

user_states = {}

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Привычки'), KeyboardButton(text='Цели')],
        [KeyboardButton(text='Рекомендации'), KeyboardButton(text='Отчеты')],
        [KeyboardButton(text='Выход')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите опцию'
)

watch_habits = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить новую привычку')],
        [KeyboardButton(text='Вернуться')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Назад'
)

async def create_habits_keyboard(user_id):
    available_habits = await get_available_habits()

    current_page = user_states.get(user_id, 0)

    start_index = current_page * 3
    end_index = start_index + 3

    habits_to_show = available_habits[start_index:end_index]

    buttons = [[KeyboardButton(text=habit)] for habit in habits_to_show]

    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(KeyboardButton(text='Назад'))
    if end_index < len(available_habits):
        navigation_buttons.append(KeyboardButton(text='Вперед'))

    if navigation_buttons:
        buttons.append(navigation_buttons)

    buttons.append([KeyboardButton(text='Вернуться')])

    habits_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    return habits_keyboard

async def create_user_habits_keyboard(user_habits, user_id):
    current_page = user_states.get(user_id, 0)

    start_index = current_page * 3
    end_index = start_index + 3
    habits_to_show = user_habits[start_index:end_index]

    buttons = [[KeyboardButton(text=habit.habit_name)] for habit in habits_to_show]

    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(KeyboardButton(text='<-'))
    if end_index < len(user_habits):
        navigation_buttons.append(KeyboardButton(text='->'))

    if navigation_buttons:
        buttons.append(navigation_buttons)

    buttons.append([KeyboardButton(text='Добавить новую привычку')])
    buttons.append([KeyboardButton(text='Вернуться')])

    habits_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    return habits_keyboard

async def create_user_habits_keyboard_double(user_habits, user_id):
    current_page = user_states.get(user_id, 0)

    start_index = current_page * 3
    end_index = start_index + 3
    habits_to_show = user_habits[start_index:end_index]

    buttons = [[KeyboardButton(text=habit.habit_name)] for habit in habits_to_show]

    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(KeyboardButton(text='<-'))
    if end_index < len(user_habits):
        navigation_buttons.append(KeyboardButton(text='->'))

    if navigation_buttons:
        buttons.append(navigation_buttons)

    habits_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    return habits_keyboard
