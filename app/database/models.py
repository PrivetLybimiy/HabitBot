from sqlalchemy import BigInteger, String, DATE, TIMESTAMP, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

db = create_async_engine(url=os.getenv('DATABASE_URL'))
async_session = async_sessionmaker(db)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True) 
    reg_date: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, default=func.now())

class Habit(Base):
    __tablename__ = 'habits'
    habit_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete="CASCADE")) 
    habit_name: Mapped[str] = mapped_column(String(255))
    habit_desc: Mapped[str] = mapped_column(Text)
    add_date: Mapped[str] = mapped_column(TIMESTAMP)

class Action(Base):
    __tablename__ = 'actions'
    action_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  
    habit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('habits.habit_id', ondelete="CASCADE")) 
    act_date: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)
    act_status: Mapped[bool] = mapped_column(Boolean, nullable=False)

class Goal(Base):
    __tablename__ = 'goals'
    goal_id: Mapped[int] = mapped_column(BigInteger, primary_key=True) 
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete="CASCADE")) 
    habit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('habits.habit_id', ondelete="CASCADE")) 
    goal_desc: Mapped[str] = mapped_column(Text)
    goal_date: Mapped[str] = mapped_column(DATE)
    goal_complete: Mapped[bool] = mapped_column(Boolean, default=False)

class AvailableHabit(Base): 
    __tablename__ = 'available_habits'
    habit_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  
    habit_name: Mapped[str] = mapped_column(String(255), nullable=False)
    habit_desc: Mapped[str] = mapped_column(Text, nullable=True) 

class Recommendation(Base):
    __tablename__ = 'recommendations'
    rec_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete="CASCADE"))  
    habit_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('habits.habit_id', ondelete="CASCADE"))
    rec_text: Mapped[str] = mapped_column(Text)
    rec_date: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)

class Report(Base):
    __tablename__ = 'reports'
    report_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id', ondelete="CASCADE")) 
    report_text: Mapped[str] = mapped_column(Text)
    report_date: Mapped[str] = mapped_column(TIMESTAMP, nullable=False)

async def async_main():
    async with db.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
