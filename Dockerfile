# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PWDEBUG=1

# Устанавливаем рабочую директорию
WORKDIR /app
RUN apt-get update
# # RUN apt-get install -y build-essential libssl-dev
# RUN apt-get clean
# RUN rm -rf /var/lib/apt/lists/*
# Копируем и устанавливаем Python-зависимости --default-timeout=100
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt --default-timeout=100 --index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install gunicorn --no-cache-dir
RUN pip install scrypt --no-cache-dir


# Копируем исходный код приложения
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение с помощью Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "project.wsgi:application"]