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

smtp сервер настроить ДЛЯ ПОЧТЫ. !!!!!

Сейчас сообщения приходят в консоль согласно настройке `settings.EMAIL_BACKEND`.


Изменить URL_REDIRECT_IF_GET_AUTHENTICATION для 301 кода

## Login
Два варианта авторизации. 
При авторизации на сервер, синхронно отправляется 2 запроса. Это вариант кодгда из \
прошлых посещений cookie сохранил данные пользователя. У нас есть индекс. \
На сервере по индексу получаем хеш-ключ. Сравниваем его с тем, что поступил их браузера.
1. Получаем токен.
2. Отправляем данные для авторизации.
**Note**: Если это повторная авторизация , то пользователя (*и ключ*) берем из cookie.\
Если вдруг cookie чистый, [смотреть тут](#coookie-если-чистый-в-браузере)\

Через метод `PATCH`, переменная `is_active` (из `requestBody`) имеет \
значение `True`. \
API: `api/v1/users/patch/<int:pk>/` \
<strike>при повторной активации пользователя на сайте, на почту пользователя</strike> \
<strike>поступает код и ссылка.</strike> \
<strike>нажимаем на ссылку, открывается страница с формой для кода.</strike>

<strike>Вводим код и проверка.</strike> 


Сам сигнал, для отправки сообщения отправляем через \
`views.py::send_message`.  
## Logout
Через метод `PATCH`, переменная `is_active` (из `requestBody`) имеет \
значение `False`. 
API: `api/v1/users/patch/<int:pk>/`
## COOKIE
1. В БД `cacher` ключи `user_session` для cookie.\
Основное назначение это определение пользователя - как index пользователя. \
Это хеш данные, синтаксис:   
```code
Это хеш данные, синтаксис:    'ISO-8859-1'
```text
<user_email>:<django_signer>
```
"[cloud_user/contribute/controler_activate.py](cloud_user/contribute/controler_activate.py)"
функция [create_signer(user)](cloud_user/contribute/sessions.py)\
Данные присваиваются переменной `user_session` и сохраняются базе данных `cacher`. \
`cacher` полученной из `settings.py::CACHES`.

`user_session` = время жизни 24 часа.
Logout - удалить ключ.

Обновление записей в hash (cacher ), по умолчанию периодично в 30 минут. [Об этом ниже](#обновление-записей-в-hash)\
Удаление записей кеша (*"`user_session_< user_id >`"*) при выходе из профиля\

Как работаем с состоянием активации пользователя - смотреть `Активация` ([из описания фронтенда](https://gitverse.ru/Workaholic/cloud_frontend)).


### COOOKIE если чистый в браузере
Если вдруг, авторизуемся, а cookie чистый.\
Обычно из куки берем индекс, и данные "`user_session`". На сервера "`user_session`"\ 
сверяем. Но главное это "`index`". \
На сервер , синхронно отправляется 2 запроса.
1. Получаем токен.
2. Отправляем данные для авторизации.

На случай если cookie пустой (*браузер почистили*), отправляем синхронно 3 запроса.    
1. Получаем токен.
2. Берем email из формы. Шифруем (*`ENCRYPT`*) и отправляем на сервер.\
На [сервера расшифровываем](cloud/services.py) и [получаем id пользователя](cloud/views.py) ("`api_get_index`").  
3. Отправляем данные для авторизации. Главное, у нас есть индекс. Сравниваем хеш паролей.\
Тут "`user_session`" не имеем. Есть индекс, email и пароль.
Если пароль введенный пользователем совпадает с hase-ем из базы данных, \
то вновь создаем ключ "`user_session`" в базе данных и сохраняем в браузере.

"`user_session`" удаляется при выходя из профиля и пользователю приходится\
авторизоваться по новой.
Всё остальное время пользователь попадает на сервис в активированном режиме.

**Note**: 
1. База данных имеет два вида кеша. Для паролей. Для ключа пользователя.
1. Кеш каждого вида/типа/категории (*не пользователя*) имеет свой шаблон маски.
1. Для определения пользователя (*если cookie пустой*), данные берем из формы и на сервере сверяем пароли кешированные.

**Note**:
1. Для ключа пользователя, на сервере есть отдельный [поток для обновления](cloud_user/tasks.py) (*с интервалом в 30 минут*).
1. Отбор пользователй для обработки проходит только тех кто имеет статус - активный и от последнего времени логирования прошло 1 и более 1-ого дня.
1. Совершаея переход между страницами сревиса, cookie браузера обновляется. Вместе с ним обновляется и ключ пользователя.
1. Для активации (при совершении событий CRUD) берем ключ и сравниваем его с тем, что хранится на сервере.
1. Пользователь сам выйдет из профиля (*`logout`*) или не будет совершать ни каких событий в течение суток - в базе данных обновляется статус (*`is_Active`= `False`*) при очередной загрузке страницы.
1. Загружаясь (*спустя сутки*), браузер запрашивает из cookie статуc пользователя и получая `False`, попадаем на главную.

### Аутентификации пользователя. 
В cookie заложен ключ `user_session` (в браузере) и `user_session_<id_usr>` в db.


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

## Logging
Код имеет логирование. Результат видно в косоли и файле 'log_putout.log
```log
[2025-02-09 14:24:42,767 767] check_log_file logs : 63 INFO - Лог-файл был обнулен, так как количество строк превысило 3000.
[2025-02-09 14:24:42,768 768] check_log_file logs : 63 INFO - Лог-файл был обнулен, так как количество строк превысило 3000.
[2025-02-09 15:24:17,985 985] trigger_reload autoreload : 266 INFO - E:\Netologe\diplom\backend\logs.py changed, reloading.
[2025-02-09 15:24:22,351 351] <module> utilites : 17 INFO - START
[2025-02-09 15:24:22,352 352] <module> utilites : 20 INFO - Received a signature
[2025-02-09 15:24:22,353 353] <module> apps : 28 INFO - START
[2025-02-09 15:24:22,354 354] <module> apps : 76 INFO - cloud_user.apps Signal WAS STARTED
[2025-02-09 15:24:23,095 95] run_with_reloader autoreload : 668 INFO - Watching for file changes with StatReloader
[2025-02-09 15:24:24,845 845] <module> sessions : 16 INFO - START
```


# Note:
 - [Проверить параллельный](#обновление-записей-в-hash) канал CACHER - логика 
обновления кеша для "`user_session_{id}`".\
При закрытии профиля и загрузки страницы (запуск логики параллельного канала) \
в db появляется 1/2 записей - "`user_session_{id}`". 

