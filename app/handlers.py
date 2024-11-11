import logging
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command
from app.database.requests import show_habbits, set_user, user_left, add_habit_to_user, get_user
from app.keyboards import create_habits_keyboard, create_user_habits_keyboard, user_states, main_menu, watch_habits
from app.metrics import COMMAND_COUNTER, ERROR_COUNTER

router = Router()
states = 0

@router.message(Command("start"))
async def cmd_start(message: Message):
    try:
        tg_id = message.from_user.id
        username = message.from_user.username

        user = await get_user(tg_id)
        if user is None:
            user_id = await set_user(tg_id, username)
        else:
            user_id = user.user_id

        logging.info(f"User {user_id} - {username} started a session")
        COMMAND_COUNTER.labels(command="start").inc()

        await message.answer(
            'Добро пожаловать в "HabitBot", бот для формирования полезных привычек',
            reply_markup=main_menu
        )
        logging.debug(f"Sent welcome message to user with id {user_id}.")
    except Exception as e:
        logging.error(f"Error in /start command for user {user_id}: {str(e)}")
        ERROR_COUNTER.inc()

@router.message(Command('help'))
async def cmd_help(message: Message):
    try:
        tg_id = message.from_user.id
        user = await get_user(tg_id)
        user_id = user.user_id

        logging.info(f"User {user_id} requested help")
        COMMAND_COUNTER.labels(command="help").inc()

        await message.answer('Вы нажали кнопку помощи', reply_markup=main_menu)
        logging.debug(f"Sent help message to user {user_id}.")
    except Exception as e:
        logging.error(f"Error in /help command for user {user_id}: {str(e)}")
        ERROR_COUNTER.inc()

@router.message(F.text == 'Привычки')
async def catalog(message: Message):
    try:
        states = 0
        tg_id = message.from_user.id
        user = await get_user(tg_id)
        user_id = user.user_id

        logging.info(f"User {user_id} opened the habits catalog")

        user_habits = await show_habbits(user_id)

        if user_habits:
            habits_keyboard = await create_user_habits_keyboard(user_habits, user_id)
            await message.answer("Ваши привычки:", reply_markup=habits_keyboard)
            logging.info(f"Displayed habits for user {user_id}.")
        else:
            await message.answer("У вас нет активных привычек. Вы можете добавить новую привычку:", reply_markup=watch_habits)
            logging.info(f"User {user_id} doesn't have habits, showed empty habits keyboard.")
    except Exception as e:
        logging.error(f"Error displaying habits for user {user_id}: {str(e)}")

@router.message(F.text == '<-')
async def previous_page(message: Message):
    states = 0
    tg_id = message.from_user.id
    user = await get_user(tg_id)
    user_id = user.user_id

    current_page = user_states.get(user_id, 0)
    if current_page > 0:
        user_states[user_id] = current_page - 1
    await catalog(message)

@router.message(F.text == '->')
async def next_page(message: Message):
    states = 0
    tg_id = message.from_user.id
    user = await get_user(tg_id)
    user_id = user.user_id

    current_page = user_states.get(user_id, 0)
    user_states[user_id] = current_page + 1
    await catalog(message)

@router.message(F.text == 'Вернуться')
async def back_from_habits(message: Message):
    try:
        await message.answer("Вы вернулись на главную", reply_markup=main_menu)
        logging.debug("User returned to main menu.")
    except Exception as e:
        logging.error(f"Error processing 'Back' button for user {message.from_user.id}: {str(e)}")
        ERROR_COUNTER.inc()

@router.message(F.text == 'Добавить новую привычку')
async def add_habit_prompt(message: Message):
    try:
        states = 1
        tg_id = message.from_user.id
        user = await get_user(tg_id)
        user_id = user.user_id

        kb = await create_habits_keyboard(user_id)

        await message.answer("Выберите привычку для добавления:", reply_markup=kb)
    except Exception as e:
        ERROR_COUNTER.inc()
        logging.error(f"Error displaying available habits: {str(e)}")
        await message.answer("Произошла ошибка при получении привычек.")

@router.message(F.text == 'Вперед')
async def next_page(message: Message):
    states = 1
    user_id = message.from_user.id
    user_states[user_id] = user_states.get(user_id, 0) + 1 
    logging.info(f"User {user_id} navigated to page {user_states[user_id]}.")
    habits_keyboard = await create_habits_keyboard(user_id)
    await message.answer("Выберите привычку:", reply_markup=habits_keyboard)

@router.message(F.text == 'Назад')
async def previous_page(message: Message):
    states = 1
    user_id = message.from_user.id
    user_states[user_id] = max(0, user_states.get(user_id, 0) - 1)
    logging.info(f"User {user_id} navigated to page {user_states[user_id]}.")
    habits_keyboard = await create_habits_keyboard(user_id)
    await message.answer("Выберите привычку:", reply_markup=habits_keyboard)

@router.message(F.text == 'Выход')
async def cmd_stop(message: Message):
    try:
        logging.info(f"User {message.from_user.id} ({message.from_user.username}) ended the session")
        await user_left(message.from_user.id)
        await message.answer("До свидания!")
    except Exception as e:
        logging.error(f"Error in /exit command for user {message.from_user.id}: {str(e)}") 

@router.message(F.text != 'Отмена' or F.text != 'Рекомендации')
async def add_habit(message: Message):
    try:
        tg_id = message.from_user.id
        user = await get_user(tg_id)
        user_id = user.user_id

        habit_name = message.text
        logging.info(f"User {user_id} is trying to add habit: {habit_name}.")
        
        user_habits = await show_habbits(user_id)

        existing_habit = next((habit for habit in user_habits if habit.habit_name == habit_name), None)

        if existing_habit and states == 1:
            await message.answer(f"Привычка '{habit_name}' уже добавлена!", reply_markup=main_menu)
        elif existing_habit and states == 0:
            habit_desc = existing_habit.habit_desc
            add_date = existing_habit.add_date.strftime("%Y-%m-%d")
            await message.answer(
                f"Привычка: {habit_name}\nОписание: {habit_desc}\nДата добавления: {add_date}",
                reply_markup=main_menu
            )
        elif not existing_habit:
            await add_habit_to_user(user_id, habit_name)
            await message.answer(f"Привычка '{habit_name}' успешно добавлена!111", reply_markup=main_menu)
            logging.info(f"User {user_id} added habit: {habit_name}.")

            user_states[user_id] = 0 

    except Exception as e:
        logging.error(f"Error adding habit '{habit_name}' for user {user_id}: {str(e)}")
        ERROR_COUNTER.inc()
