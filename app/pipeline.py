import pandas as pd
from sqlalchemy import select
from app.database.models import async_session, AvailableHabit

def extract_data_from_excel(file_path: str) -> pd.DataFrame:
    data = pd.read_excel(file_path)
    return data

def transform_data(data: pd.DataFrame):
    data['habit_name'] = data['habit_name'].astype(str).str.strip()
    data['habit_desc'] = data['habit_desc'].astype(str).str.strip()
    return data

async def load_data_to_db(data: pd.DataFrame):
    async with async_session() as session:
        async with session.begin():
            for _, row in data.iterrows():
                if pd.notna(row['habit_name']):
                    existing_habit = await session.execute(
                        select(AvailableHabit).where(AvailableHabit.habit_name == row['habit_name'])
                    )
                    if existing_habit.scalars().first() is None:
                        available_habit = AvailableHabit(
                            habit_name=row['habit_name'],
                            habit_desc=row['habit_desc'] if pd.notna(row['habit_desc']) else None
                        )
                        session.add(available_habit)

            await session.commit()

async def etl_pipeline(file_path: str):
    data = extract_data_from_excel(file_path)
    if not data.empty:
        data = transform_data(data)
        await load_data_to_db(data)
