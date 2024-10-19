import os
import subprocess
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from app.database.models import Base

# Получение URL базы данных и пароля из переменных окружения
db_url = os.getenv('DATABASE_URL')
PGPASSWORD = os.getenv("PGPASSWORD")
db = create_async_engine(url=db_url)

BACKUP_DIR = r"C:/bd_backup"

# Создание директории для резервных копий, если она не существует
os.makedirs(BACKUP_DIR, exist_ok=True)

async def backup_database():
    date = datetime.now().strftime("%Y%m%d_%H%M")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{date}.sql")

    dump_command = [
        r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe",
        "-h", "localhost",
        "-U", "postgres",
        "-d", "HabitBot",
        "-F", "c",
        "-f", backup_file
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = PGPASSWORD

    try:
        subprocess.run(dump_command, env=env, check=True, capture_output=True)
        print(f"Резервная копия успешно создана: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании резервной копии: {e.stderr.decode()}")

async def create_db_schema():
    async with db.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

async def main():
    await create_db_schema()
    await backup_database()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
