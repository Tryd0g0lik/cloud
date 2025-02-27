# Используем официальный образ Nginx
FROM nginx:alpine
RUN rm -rf /etc/nginx/conf.d/default.conf || echo "default.conf не существует"
RUN mkdir -p /etc/nginx/conf.d

# Копируем конфигурацию Nginx
COPY default.conf /etc/nginx/conf.d
# Открываем порт для Nginx
# EXPOSE 80
