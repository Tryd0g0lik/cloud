# Используем официальный образ Nginx
FROM nginx:alpine
RUN rm -rf /etc/nginx/conf.d/default.conf || echo "default.conf не существует"
RUN mkdir -p /etc/nginx/conf.d

# Копируем конфигурацию Nginx
#COPY --from=builback /templates/users/ /usr/share/nginx/html/
COPY default.conf /etc/nginx/conf.d/default.conf
#EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]