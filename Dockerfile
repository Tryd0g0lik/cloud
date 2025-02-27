# Используем официальный образ Python
FROM python:3.10
RUN apt-get update && apt install -y python3-venv
# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PWDEBUG=1

# Устанавливаем рабочую директорию
WORKDIR /app
#RUN apt-get update
# # RUN apt-get install -y build-essential libssl-dev
# RUN apt-get clean
# RUN rm -rf /var/lib/apt/lists/*
# Копируем и устанавливаем Python-зависимости --default-timeout=100
#  --default-timeout=30 --upgared --index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn --no-cache-dir
RUN pip install scrypt --no-cache-dir
RUN mkdir -p media && mkdir -p media/cards && mkdir -p media/uploads

# Копируем исходный код приложения
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение с помощью Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "project.wsgi:application"]