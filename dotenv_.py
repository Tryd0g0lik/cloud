import os

import dotenv

dotenv.load_dotenv()

SECRET_KEY_ = os.getenv("SECRET_KEY", "")
APP_PROTOKOL = os.getenv("APP_PROTOKOL", "https")
APP_SERVER_HOST = os.getenv("APP_SERVER_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cloud")
EMAIL_PORT_ = os.getenv("EMAIL_PORT", "1025")
EMAIL_HOST_USER_ = os.getenv("EMAIL_PORT", "")
EMAIL_HOST_PASSWORD_ = os.getenv("EMAIL_HOST_PASSWORD", "")
DSN = f"postgresql://{POSTGRES_USER}:\
{POSTGRES_PASSWORD}@\
{POSTGRES_HOST}:\
{POSTGRES_PORT}/\
{POSTGRES_DB}"
