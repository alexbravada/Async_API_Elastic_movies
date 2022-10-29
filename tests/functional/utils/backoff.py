from functools import wraps
from time import sleep

from psycopg2 import OperationalError
import logging as log


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, exception=OperationalError, log=log):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param exception:
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            current_sleep_time = start_sleep_time
            while True:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    log.error(f'Ожидаем запуска к сервису {func.__name__}, {current_sleep_time} {e}')
                    current_sleep_time = factor * current_sleep_time \
                        if factor * current_sleep_time < border_sleep_time else border_sleep_time
                    sleep(current_sleep_time)

        return inner

    return wrapper
