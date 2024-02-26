"""
Сканер каталога. Получает на вход путь до директории на ПК.
"""

import argparse
import os
import logging
import datetime
from collections import namedtuple
from logging.handlers import RotatingFileHandler


class DirLogger():
    """
    Класс логера сканера каталогов
    """
    DEBUG: int = logging.DEBUG
    INFO: int = logging.INFO
    WARNING: int = logging.WARNING
    ERROR: int = logging.ERROR
    CRITICAL: int = logging.CRITICAL
    MAX_FILE_SIZE = 1_000_000
    LOG_FILE_COUNT = 10

    def __init__(self, **kwargs):
        """
        Класс логера сканера каталогов.
        Создает лог-файл с текущей датой в названии в каталоге запуска скрипта.
        Аргументы:
            level: int      - уровень логирования. По-умолчанию, DEBUG
            encoding: str   - кодировка файла. По-умолчанию UTF-8
        """
        log_level = kwargs.get('level', self.DEBUG)
        log_file_encoding = kwargs.get('encoding', 'utf-8')
        log_file_name = f'dir_data__{str(datetime.datetime.now().date())}.log'
        log_file_dir = os.path.dirname(os.path.abspath(__file__))

        handler = RotatingFileHandler(
            os.path.join(log_file_dir, log_file_name),
            mode='w',
            maxBytes=self.MAX_FILE_SIZE,
            backupCount=self.LOG_FILE_COUNT,
            encoding='utf-8')
        handler.setFormatter(logging.Formatter(
            "%(levelname)s [%(asctime)s]: %(message)s"))
        self._logger = logging.getLogger(log_file_name)
        self._logger.setLevel(log_level)
        self._logger.addHandler(handler)

    def log_message(self, message: str, level: int = INFO) -> None:
        """
        Добавляет сообщения в лог-файл.
        Аргументы:
            message: str        - Сообщение
            level: int          - Уровень сообщения (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if level == self.INFO:
            self._logger.info(message)
        elif level == self.WARNING:
            self._logger.warning(message)
        elif level == self.ERROR:
            self._logger.error(message)
        else:
            self._logger.critical(message)


class DirData ():
    """
    Класс сканера каталога.
    """

    def __init__(self, **kwargs):
        """
        Класс сканера каталога.
        Аргументы конструктора:
            path: str           - путь к каталогу, который необходимо просканировать
            recursive: bool     - выполнить рекурсивное сканирование подкаталогов
        """
        self._path = kwargs.get('path', None)
        self._recursive = kwargs.get('recursive', False)
        self._data = []
        self._logger = DirLogger()
        self._logger.log_message('Объект успешно инициализирован.')

    def run(self) -> int:
        """
        Выполняет сканирование файлов и подкаталогов в каталоге.
        Аргументы:
            -
        Возвращает:
            int     - код ошибки. 0, если сканирование прошло успешно
        """
        data = []
        if not os.path.isdir(self._path):
            self._logger.log_message(
                'Каталог не найден. Прекращаю работу.',
                level=self._logger.CRITICAL)
            return 404
        try:
            self._data = self._get_dir_data(self._path)
            self._logger.log_message('Работа успешно завершена.')
            return 0
        except PermissionError:
            self._logger.log_message(
                'Доступ запрещен. Прекращаю работу.',
                level=self._logger.CRITICAL)
            return 403

    def get_data(self) -> list:
        """
        Возвращает данные, полученные при сканировании каталога(каталогов)
        Аргументы:
            -
        Возвращает:
            list[namedtuple('File', 'name ext is_dir parent_name')]
        """
        return self._data

    def _get_dir_data(self, path: str) -> list:
        """
        Получает путь к каталогу и возвращает список файлов и каталогов в нем.
        Аргументы:
            path: str   - путь к каталогу
        Возвращает:
            list[namedtuple('File', 'name ext is_dir parent_name')]
        """
        data = []
        file_tpl = namedtuple('File', 'name extension is_dir parent')
        parent = os.path.abspath(path)
        self._logger.log_message(f"Сканирую каталог '{parent}'")
        for file_obj in os.listdir(parent):
            dir_data = []
            is_dir = os.path.isdir(file_obj)
            file_name = os.path.basename(file_obj)
            file_ext = ''
            if not is_dir:
                file_name, file_ext = os.path.splitext(file_name)
                file_ext = file_ext.replace('.', '')
            elif self._recursive:
                dir_data = self._get_dir_data(os.path.join(parent, file_obj))
                self._logger.log_message(
                    f"Сканирую каталог '{parent}' (продолжаю прерванное сканирование)")
            file_obj_data = file_tpl(name=file_name, extension=file_ext,
                                     is_dir=is_dir, parent=parent)
            data.append(file_obj_data)
            self._logger.log_message(f'Обработка объекта: {file_obj_data}')
            data += dir_data
        return data


parser = argparse.ArgumentParser(description='Сканер каталога.')
parser.add_argument('--path', type=str, required=True,
                    help='Путь к сканируемому каталогу.')
parser.add_argument('--recursive', type=str,
                    help='Рекурсивная обработка подкаталогов (Y/N)')
args = parser.parse_args()
pre_kwargs = dict()
pre_kwargs['path'] = args.path
recursive = args.recursive
pre_kwargs['recursive'] = False
if isinstance(recursive, str) and (recursive.lower() == 'y' or recursive.lower() == 'yes'):
    pre_kwargs['recursive'] = True

app = DirData(**pre_kwargs)
app.run()
