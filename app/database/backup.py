import os
import subprocess
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from app.database.models import Base

db_url = os.getenv('DATABASE_URL')
PGPASSWORD = os.getenv("PGPASSWORD")
db = create_async_engine(url=db_url)

BACKUP_DIR = "/app/bd_backup"
os.makedirs(BACKUP_DIR, exist_ok=True)

async def backup_database():
    date = datetime.now().strftime("%Y%m%d_%H%M")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{date}.sql")

    dump_command = [
        "pg_dump", 
        "-h", "postgres",        # Имя сервиса базы данных в docker-compose
        "-U", "postgres",        # Имя пользователя
        "-d", "HabitBot",        # Имя базы данных
        "-F", "c",               # Формат резервной копии
        "-f", backup_file        # Путь к файлу резервной копии
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = PGPASSWORD

    result = subprocess.run(dump_command, env=env, check=True, capture_output=True)
    if result.returncode == 0:
        logging.info(f"Резервная копия успешно создана: {backup_file}")
    else:
        logging.error(f"Ошибка при создании резервной копии: {result.stderr.decode()}")


async def create_db_schema():
    async with db.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

async def main():
    await create_db_schema()
    await backup_database()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
