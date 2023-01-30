import os
import logging
from logging.handlers import RotatingFileHandler

# Logging Configs
log_size = 10
backup_count = 30
delay = 0

LEVEL = 20

"""
logging.CRITICAL = 50
logging.FATAL = CRITICAL
logging.ERROR = 40
logging.WARNING = 30
logging.WARN = WARNING
logging.INFO = 20
logging.DEBUG = 10
logging.NOTSET = 0
"""


class Log_Facilitator:
    def __init__(self, logFilePath, loggerName, level=LEVEL):
        self.__log_file_path = self._init_log_file_path(logFilePath)
        self.__level = level
        self.__log_format = logging.Formatter(
            "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]:%(message)s"
        )
        self.__rotating_file_handler = self._init_rotating_file_handler()
        self.logger = self._init_logger(loggerName)

    def _init_log_file_path(self, path):
        current_directory = os.getcwd()
        folder = "logs"
        directory = os.path.join(current_directory, folder)
        file_name = path + ".log"
        path = os.path.join(directory, file_name)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        if not os.path.isfile(path):
            with open(path, "a") as log:
                log.write("New log file started.\n")
        return path

    def _init_rotating_file_handler(self):
        rotating_file_handler = RotatingFileHandler(
            self.__log_file_path,
            mode="a",
            maxBytes=log_size * 1024 * 1024,
            backupCount=backup_count,
            encoding=None,
            delay=delay,
        )
        rotating_file_handler.setFormatter(self.__log_format)
        rotating_file_handler.setLevel(self.__level)
        return rotating_file_handler

    def _init_logger(self, loggerName):
        logger = logging.getLogger(loggerName)
        logger.setLevel(self.__level)
        logger.addHandler(self.__rotating_file_handler)
        logger.propagate = False
        return logger


api_logger = Log_Facilitator("api", "main.py")
