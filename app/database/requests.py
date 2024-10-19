import json
import logging
from sqlalchemy import func
from sqlalchemy.future import select
from app.database.models import async_session, User, Habit, AvailableHabit
from app.metrics import REQUEST_COUNTER, ACTIVE_USERS
from app.conf.redis import redis_client

active_users = set()

async def get_user(tg_id: int):
    logging.debug(f"Getting user with tg_id: {tg_id}")
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar()
        
        if user:
            logging.info(f"User found: {user.user_id}")
            return user
        else:
            user_id = await set_user(tg_id, f"User_{tg_id}")
            new_user = await session.get(User, user_id)
            logging.info(f"New user added: {new_user.user_id}")
            return new_user

async def set_user(tg_id: int, username: str):
    logging.debug(f"Setting user {username} with tg_id: {tg_id}")
    async with async_session() as session:
        try:
            user = User(tg_id=tg_id, username=username)
            session.add(user)
            REQUEST_COUNTER.inc()
            await session.commit()
            logging.info(f"User {user.user_id} added to the database.")
            return user.user_id
        except Exception as e:
            logging.error(f"Error while setting user {tg_id}: {str(e)}")
            await session.rollback()

async def show_habbits(user_id: int):
    logging.debug(f"Showing habits for user {user_id}")
    async with async_session() as session:
        REQUEST_COUNTER.inc()
        try:
            result = await session.execute(select(Habit).where(Habit.user_id == user_id))
            habits = result.scalars().all()
            
            if habits:
                logging.info(f"User {user_id}'s habits: {[habit.habit_name for habit in habits]}")
                return habits
            else:
                logging.info(f"User {user_id} has no habits.")
                return []
        except Exception as e:
            logging.error(f"Error displaying habits for user {user_id}: {str(e)}")
            return []

async def get_available_habits():
    logging.debug("Getting available habits")
    async with async_session() as session:
        REQUEST_COUNTER.inc()
        result = await session.scalars(select(AvailableHabit))
        habits = result.all()
        logging.info(f"Available habits: {[habit.habit_name for habit in habits]}")
        return [habit.habit_name for habit in habits]
    
async def add_habit_to_user(user_id: int, habit_name: str):
    logging.debug(f"Adding habit '{habit_name}' for user {user_id}")
    async with async_session() as session:
        try:
            available_habit = await session.execute(
                select(AvailableHabit).where(AvailableHabit.habit_name == habit_name)
            )
            available_habit = available_habit.scalar_one_or_none()

            if available_habit:
                habit_desc = available_habit.habit_desc
                habit = Habit(user_id=user_id, habit_name=habit_name, habit_desc=habit_desc, add_date=func.now())
                session.add(habit)
                REQUEST_COUNTER.inc()
                await session.commit()

                redis_client.rpush(f"user_habits:{user_id}", habit_name)

                active_users.add(user_id)
                ACTIVE_USERS.set(len(active_users))
                
                logging.info(f"User {user_id} added habit {habit_name}.")
            else:
                logging.error(f"Available habit '{habit_name}' not found.")
        except Exception as e:
            logging.error(f"Error adding habit {habit_name} for user {user_id}: {str(e)}")
            await session.rollback()

async def user_left(user_id: int):
    logging.debug(f"User {user_id} left the session.")
    if user_id in active_users:
        active_users.remove(user_id)
        ACTIVE_USERS.dec()
        logging.info(f"User {user_id} marked as inactive.")
