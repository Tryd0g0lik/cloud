"""
This page has a logics for logging.
Data result from logging we can see in console and in 'log_putout.log' file.
"""

import logging


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
    file_handler = logging.FileHandler(log_file,  encoding='utf-8')
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
