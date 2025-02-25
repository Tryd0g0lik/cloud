"""
This page is include the module for logging.
Data result from logging we can see in console and in 'log_putout.log' file.
The 'log_file'  parameter for setting the file's  name '*.log'.
Default the name is 'log_putout.log
"""

import logging
import threading
import time


def configure_logging(level: int = logging.INFO, log_file="log_putout.log") -> None:
    """
    For a beginning work
    :param level:
    :param log_file:
    :return:
    ```py
        import logging

        from rabbit.logs import configure_logging \n
        log = logging.getLogger(__name__) \n
        configure_logging(logging.INFO) \n
        log.info("run_consumer start ")

        // [2024-12-12 16:23:56,991: INFO/MainProcess] run_consumer start '
    ````
    """
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)

    # Создание обработчика для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    # Форматирование логов
    formatter = logging.Formatter(
        "[%(asctime)s %(msecs)d] %(funcName)s %(module)s : %(lineno)d %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # Настройка корневого логгера
    logging.basicConfig(level=level, handlers=[file_handler, console_handler])
    # Запуск проверки файла логов в отдельном потоке
    threading.Thread(target=check_log_file, args=(log_file,), daemon=True).start()


def check_log_file(log_file: str) -> None:
    """
    Проверяет количество строк в файле логов каждые 30 минут.
    Если количество строк превышает 3000, файл обнуляется.
    :param log_file: Имя файла логов
    """
    while True:
        time.sleep(1800)  # Ожидание 30 минут
        try:
            with open(log_file, "r", encoding="utf-8") as file:
                lines = file.readlines()
                if len(lines) >= 3000:
                    # Обнуление файла
                    with open(log_file, "w", encoding="utf-8") as f:
                        f.truncate()
                    logging.info(
                        "Лог-файл был обнулен, так как количество строк превысило 3000."
                    )
        except Exception as e:
            logging.error(f"Ошибка при проверке лог-файла: {e}")


class Logger:
    def print_class_name(self):
        """Return class-name"""
        return self.__class__.__name__
