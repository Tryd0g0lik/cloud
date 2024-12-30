# Используем официальный образ Python
FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PWDEBUG=1
ENV APP_POSTGRES_HOST=localhost
ENV APP_POSTGRES_PORT=5432
ENV APP_PROTOKOL=http
ENV APP_POSTGRES_PASS=123
ENV APP_POSTGRES_LOGIN=postgres
ENV APP_POSTGRES_DBNAME=library
ENV SECRET_KEY=562778be-3e23-407e-8544-f5bc184cb547
RUN apt update
RUN apt install -y python3-venv
RUN python3 -m venv /opt/venv
# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install --upgrade ./venv/bin/pip
RUN python3 -m venv venv
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Команда для запуска приложения
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]