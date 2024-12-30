import os

import dotenv

dotenv.load_dotenv()

SECRET_KEY_ = os.getenv("SECRET_KEY", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
APP_PROTOKOL = os.getenv("APP_PROTOKOL", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cloud")
DSN = f"postgresql://{POSTGRES_USER}:\
{POSTGRES_PASSWORD}@\
{POSTGRES_HOST}:\
{POSTGRES_PORT}/\
{POSTGRES_DB}"
