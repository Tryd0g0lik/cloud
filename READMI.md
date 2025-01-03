# CLOUD_USER
Настраивая файл `settings.py` меняем базовую модель `User` на `UserRegister`. \
`UserRegister` наследуется от `User`.

## Регистрация
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

## Email-message
`app.py` К сервису подачи сигнала (сигнал подаем когда требуется отправить \
сообщение на почту для аутентификации пользователя) подключаем \
`send_activation_notificcation` функцию отправления сообщения на почту.

Из текста `activation_letter_subject.txt` (А) создаем шаблон письма для предложения \
аутентификации и `email/activation_letter_body.txt` шаблон подтверждения \
аутентификации.

Сам сигнал, для отправки сообщения отправляем через \
`RegisterUserSerializer.create`.  

Сообщение (письмо) А имеет ссылку с подписью из `Signer` \
(из `send_activation_notificcation`). \
В `controler_activate.user_activate` - проверка подписи (`sign` - ниже). Сама функция \
срабатывает при клике по ссылке в письме.

## Signal (Сигнал) - 'sign' 
Когда создаём сигнал (`cloud_user/contribute/utilites.py` ), к параметру \
`sign` присваеваем значение. 

В данном случаем значением является `first_name` из модели \
подели `UserRegister`. \
Далее `first_name`  используем в:
- письмах;
- `cloud_user/contribute`;
- подписи `Signer` (`utilites.py`,`controler_activate.py`) 

## Сообщение аутентификации

Запускаем метод `email_user`, из базовой модели пользователя, отправляет\
сообщение используя `[send_mail](https://docs.djangoproject.com/en/5.1/topics/email/)`.

smtp сервер настроить ДЛЯ ПОЧТЫ.

Сейчас сообщения призодят в консоль согласно настройки `settings.EMAIL_BACKEND`.



