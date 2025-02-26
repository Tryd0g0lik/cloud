# Используем официальный образ Nginx
FROM nginx:alpine
RUN rm -rf /etc/nginx/conf.d/default.conf || echo "default.conf не существует"
RUN rm -rf /etc/nginx/conf.d
RUN mkdir -p /etc/nginx
# Копируем конфигурацию Nginx
#COPY ./nginx.conf /etc/nginx/nginx.conf
# Открываем порт для Nginx
# EXPOSE 80
