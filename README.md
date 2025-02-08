D работе 

[frontend](https://github.com/Tryd0g0lik/cloud_frontend)

# CLOUD_USER
1. Настраивая файл `settings.py` меняем базовую модель `User` на `UserRegister`. \
`UserRegister` наследуется от `User`.

2. Согласно описания задачи (ТЗ), термин `аутентификация` подразумевает\
логирование (регистрацию) пользователя на сайте.\
Код реализован с учетом разделения на:
- `аутентификация` - когда пользователь получает реферальную ссылку на почту \
при первичной регистрации нового пользователя на сайте.
- `регистрация`/`login`/`логирование`  на сайте при повторной активации \
аккаунта (профиля).\


## Регистрация
1. Почта указанная при регистрации не меняется.
2. При регистрации, на почту юзера отправляется ссылка для \
аутентификации. \
Ссылка имеет свой url.
Юзер кликает на ссылку .

Далее `**/contribute/controler_activate.py`\
Проходит проверку статуса аутентификации.\ (ВРЕМЯ ЖИЗНИ ССЛЫКИ добавить)
Если `is_activated` имеет TRUE, редирект\
на страницу `URL_REDIRECT_IF_NOTGET_AUTHENTICATION`. \
Иначе редирект на страницу `URL_REDIRECT_IF_GET_AUTHENTICATION`.\
Если FALSE, меняем:
- `is_activated` на TRUE;
- `is_active` на TRUE.
### Password !!!
/* ------ Есть заглушка ------ */
В django поступает 1 пароль из фронта. \
На фронте - пароль проходит через базовую проверку. Пароль1 == Пароль2 и длина. \
Из фронта в бэк , пароль уходит без хеша в синтаксисе\
```code
<algorithm>$<iterations>$<salt>$<hash>
```
Проверка на бэке.\ 
`cloud_user/views.py::UserView.create` `hash_password` убрать . сейчас как заглушка для хэша данных 

Далее редирект на страниу `URL_REDIRECT_IF_GET_AUTHENTICATION`.\
Юзер попадет на страницу уже АВТОРИЗОВАНым.
Дополнительно сохраняем [данные в COOKIE](#cookie) 



## Email-message
`app.py` К сервису подачи сигнала (сигнал подаем когда требуется отправить \
сообщение на почту для аутентификации пользователя) подключаем \
`send_activation_notificcation` функцию отправления сообщения на почту.

Из текста `activation_letter_subject.txt` (А) создаем шаблон письма для предложения \
аутентификации и `email/activation_letter_body.txt` шаблон подтверждения \
аутентификации.


Сообщение (письмо) А имеет ссылку с подписью из `Signer` \
(из `send_activation_notificcation`). \
В `controler_activate.py::user_activate` - проверка подписи (`sign` - ниже). \
Сама функция срабатывает после клике по ссылке из письма юзера.

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


Изменить URL_REDIRECT_IF_GET_AUTHENTICATION для 301 кода

## Login
Через метод `PATCH`, переменная `is_active` (из `requestBody`) имеет \
значение `True`. \
API: `api/v1/users/patch/<int:pk>/` \
<strike>при повторной активации пользователя на сайте, на почту пользователя</strike> \
<strike>поступает код и ссылка.</strike> \
<strike>нажимаем на ссылку, открывается страница с формой для кода.</strike>

Вводим код и проверка. 


Сам сигнал, для отправки сообщения отправляем через \
`views.py::send_message`.  
## Logout
Через метод `PATCH`, переменная `is_active` (из `requestBody`) имеет \
значение `False`. 
API: `api/v1/users/patch/<int:pk>/`
## COOKIE
1. В БД `cacher` ключи `user_session` для cookie.\
Основное назначение это определение пользователя - как index пользователя. \
<<<<<<< HEAD
Это хеш данные, синтаксис:   
```code
=======
Это хеш данные, синтаксис:    'ISO-8859-1'
```text
>>>>>>> profile
<user_email>:<django_signer>
```
"[cloud_user/contribute/controler_activate.py](cloud_user/contribute/controler_activate.py)"
функция [create_signer(user)](cloud_user/contribute/sessions.py)\
Данные присваиваются переменной `user_session` и сохраняются базе данных `cacher`. \
`cacher` полученной из `settings.py::CACHES`.

`user_session` = время жизни 24 часа.
Logout - удалить ключ.

Обновление записей в hash (cacher ), по умолчанию периодично в 30 минут. [Об этом ниже](#обновление-записей-в-hash)\
Удаление при выходе из профиля\
    Если юзер закрыл окно без logout , при следующем открытии окна , поиск старого ключа и обновление.\
    Подумать об использовании ключа сессии и таблицы из нее.\
    Ключ кешировать , для практики

Обращаясь из фронта ключ получаем из данных куки. \
Из хеша получаем емайл\
от емайла получаем idm и сравниваем . Так получили подлиность юзера\
Создать функцию at session ??? 

### COOOKIE если чистый в браузере
Если вдруг, авторизуемся, а cookie чистый.\
Обычно из куки берем индекс, и данные "`user_session`". На сервера "`user_session`"\ 
сверяем. Но главное это "`index`". \
На сервер , синхронно отправляется 2 запроса.
1. Получаем токен.
2. Отправляем данные для авторизации.

На случай если cookie пустой, отправляем синхронно 3 запроса.  
1. Получаем токен.
2. Берем email из формы. Шифруем и отправляем на сервер.\
На [сервера расшифровываем](cloud/services.py) и [получаем id пользователя](cloud/views.py) ("`api_get_index`").  
3. Отправляем данные для авторизации. Главное, у нас есть индекс. \
Тут "`user_session`" не имеем. Есть индекс, email и пароль.
Если пароль введенный пользователем совпадает с hase-ем из базы данных, \
то вновь создаем ключ "`user_session`" в базе данных и сохраняем в браузере.

"`user_session`" удаляется при выходя из профиля и пользователю приходится\
авторизоваться по новой.
Всё остальное время пользователь попадает на сервис в активированном режиме.


### Обновление записей в hash
[Эта задача](cloud_user/tasks.py) проверяет время жизни строки в кэше (это 'cacher' из 'settings.py').\
Выбирает пользователей по ID от 'quantity' до 'number' и проверяет время жизни.\
Затем изменяет время жизни для пользователя, где 'last_login' (из модели 'UserRegister') меньше, чем 'hash_live_time'.\
Или вовсе удаляет если 'is_active' (из модели 'UserRegister') = False. Это \
контрольное удаление (мало ли).  
Выборка пользователей из базы данных проходит по диапазону из 'number'.\

Запуск каждые 30 минут в параллельном потоке, на основную работу приложения не влияет.


## FILES
- Все методы асинхронные.
- Модель `FileStorage` из `cloud_file/models.py`
- Каждый файл получает два маршрута для сохранения.
    - `card/` - временной хранилище. Файл проходит проверку на дублирование.\  
Если один файл просто переименовать - все равное будет считать дублем.\
Файл с изменениеями в содержимом/контенте - считается как новый файл.\
Проверка модулем `hashlib.md5`из `cloud/hashers.py::md5_chacker` \
(`cloud_file/views.py::FileStorageViewSet.compare_twoFiles`).  
    - `uploads/` - конечное хранилище файла.
Note: Если два разных пользователя загрузят один файл, на сервере 
будет дублированный файл. Проверка в границах коллекции одного пользователя.
    - маршрут имеет синтаксис
```code
<uploads>/<user_id>/<year_upload>/<month_upload>/<day_upload>/File_name.now
```
### Загрузка файла на сервер
`FileStorageViewSet.create`.\
- загрузка любого расширенияж
- проверки и ограничения по весу файла - нет.
- тут же создаём ту самую специальную ссылку, модулем `uuid.uuid4`.  
Note: `cloud_file/views.py::FileStorageViewSet.generate_link` Выполняет задачу \
из ТЗ - создает URL для скачивания. В ТЗ нет условия , что при каждом \
обращении на сервер должна генерироваться новая ссылка. Тем самым условие выполнено.

### Права пользователя

Интерфейс включающий проверку прав пользователя для успешного завершения:
- загрузка файла
- список файлов
- получить один файл
- удалить файл
- переименовать файл
- обновить комментарий к файлу
- генерация специальной ссылки
    
Интерфейс исключающий проверку прав пользователя:
- скачать файл по специальной ссылке.


<<<<<<< HEAD
=======
# Note:
 - [Проверить параллельный](#обновление-записей-в-hash) канал CACHER - логика 
обновления кеша для "`user_session_{id}`".\
При закрытии профиля и загрузки страницы (запуск логики параллельного канала) \
в db появляется 1/2 записей - "`user_session_{id}`". 

>>>>>>> profile
