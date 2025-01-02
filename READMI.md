При регистрации, на почту юзера отправляется ссылка для \
аутентификации. \
Сссылка имеет свой url.
Юзер кликает на ссылку на ссылку.

Далее `**/contribute/controler_activate.py`\
Проходит проверку статуса аутентификации.\
Если `is_activated` имеет TRUE, запуск редиректа\
на `URL_REDIRECT_IF_NOTGET_AUTHENTICATION`. \
 
Если FALSE, меняем:
- `is_activated` на TRUE;
- `is_active` на TRUE.

Далее запуск редиректа на редирект на `URL_REDIRECT_IF_GET_AUTHENTICATION`.
Юзер попадет на страницу уже АВТОРИЗОВАНым !!!

