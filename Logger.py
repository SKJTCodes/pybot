import atexit
import gzip
import logging
import logging.config
import os
import pathlib
import shutil
import socket
import sys
from pathlib import Path
from typing import Union

import helper as h


class Log:
    def __init__(self,
                 log_path: Union[str, pathlib.PurePath] = None,
                 desc=None,
                 con_lvl: str = "INFO",
                 log_lvl: str = "DEBUG",
                 handler_gz: list = None) -> None:
        """
        Specify Logging Parameters
        :param log_path: can only be str of Path object. Base path to be insert log files
        :param con_lvl: console messages display level
        :param log_lvl: loggin file message level
        :param handler_gz: specify which handler to zip else only 'log' handler is zipped.
        """
        assert isinstance(log_path, (str, pathlib.PurePath)), "log_path can only be a string or Path object"

        if isinstance(log_path, str):
            log_path = Path(log_path)
        log_path.mkdir(parents=True, exist_ok=True)

        self.log_path = log_path
        self.base = h.getparentfname(suffix=False)
        self.base_path = log_path / self.base
        self.handler_gz = handler_gz

        formatters = {
            'detailed': {
                'class': 'logging.Formatter',
                'format': '%(asctime)s %(levelname)-8s %(message)s',
                'datefmt': '%Y%m%d-%H%M.%S'
            },
            'simple': {
                'class': 'logging.Formatter',
                'format': '%(levelname)-8s %(message)s',
                'datefmt': '%Y%m%d-%H%M.%S'
            }
        }
        handlers = {
            # show INFO and aboce in console messages
            'console': {
                'class': 'logging.StreamHandler',
                'level': con_lvl,
                'formatter': 'simple'
            },
            # log DEBUG messages and above into a file
            'log': {
                'class': 'logging.FileHandler',
                'filename': f"{self.base_path.with_suffix('.log.txt')}",
                'mode': 'w',
                'level': log_lvl,
                'formatter': 'detailed',
                'encoding': 'utf-8'
            }
        }
        loggers = {
            f"{self.base}": {
                'level': 'DEBUG',
                'handlers': ['console', 'log'],
                'propogate': False
            }
        }

        # Log Settings
        self.config = {
            'version': 1,
            'formatters': formatters,
            'handlers': handlers,
            'loggers': loggers
        }

        # initialize log object
        logging.config.dictConfig(self.config)
        log = self.get_logger()

        # add exception handling
        # https://stackoverflow.com/questions/8050775/using-pythons-logging-module-to-log-all-exceptions-and-errors/8054179#8054179
        # https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python/16993115#16993115
        def exception_handler(exc_type, exc_value, exc_tb):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_tb)
                return
            logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

        sys.excepthook = exception_handler

        # set color to output
        if os.name == 'nt':
            logging.StreamHandler.emit = self._add_color_to_emit_windows(logging.StreamHandler.emit)
        else:
            logging.StreamHandler.emit = self._add_color_to_emit_ansi(logging.StreamHandler.emit)

        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname_ex(hostname)[2]
        self.today_datetime = h.date_delta(fmt="%Y%m%d-%H%M.%S")
        info = {
            'Desc': desc,
            'Module': self.base,
            'Date': self.today_datetime,
            'User': h.getuser(),
            'Name': h.getusername(),
            'Host': hostname,
            'IP': ip_addr,
            'cwd': os.getcwd(),
            "log dir": log_path
        }

        info_fmt = '{:>8} : {}'
        for logger in [log]:
            for key, val in info.items():
                logger.info(info_fmt.format(key, val))
                # when script runs finish run the _export function
                atexit.register(self._export)

    def get_logger(self, suffix=""):
        return logging.getLogger(f"{self.base}{suffix}")

    def _export(self):
        """
        Specify where to save the history of logs
        """
        if self.handler_gz is None:
            self.handler_gz = ['log']

        for handler in self.handler_gz:
            src = Path(self.config['handlers'][handler]['filename'])
            dst = self.log_path / f"{src.name.split('.')[0]}-{self.today_datetime}.{h.getuser()}" \
                                  f"{''.join(src.suffixes)}.gz"
            with open(src, 'rb') as f_in:
                with gzip.open(dst, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

    @staticmethod
    def _add_color_to_emit_windows(fn):
        def _set_color(self, code):
            import ctypes
            # Constants from the windows API
            self.STD_OUTPUT_HANDLE = -11
            hdl = ctypes.windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE)
            ctypes.windll.kernel32.SetConsoleTextAttribute(hdl, code)

        setattr(logging.StreamHandler, '_set_color', _set_color)

        def new(*args):
            FOREGROUND_BLUE = 0x0001  # text color contains blue.
            FOREGROUND_GREEN = 0x0002  # text color contains green.
            FOREGROUND_RED = 0x0004  # text color contains red.
            FOREGROUND_WHITE = FOREGROUND_BLUE | FOREGROUND_GREEN | FOREGROUND_RED

            # wincon.h
            FOREGROUND_GREEN = 0x0002
            FOREGROUND_RED = 0x0004
            FOREGROUND_MAGENTA = 0x0005
            FOREGROUND_YELLOW = 0x0006
            FOREGROUND_INTENSITY = 0x0008  # foreground color is intensified.

            BACKGROUND_YELLOW = 0x0060
            BACKGROUND_INTENSITY = 0x0080  # background color is intensified.

            levelno = args[1].levelno
            if levelno >= 50:
                color = BACKGROUND_YELLOW | FOREGROUND_RED | FOREGROUND_INTENSITY | BACKGROUND_INTENSITY
            elif levelno >= 40:
                color = FOREGROUND_RED | FOREGROUND_INTENSITY
            elif levelno >= 30:
                color = FOREGROUND_YELLOW | FOREGROUND_INTENSITY
            elif levelno >= 20:
                color = FOREGROUND_GREEN
            elif levelno >= 10:
                color = FOREGROUND_MAGENTA
            else:
                color = FOREGROUND_WHITE

            args[0]._set_color(color)
            ret = fn(*args)
            args[0]._set_color(FOREGROUND_WHITE)
            # print "after"
            return ret

        return new

    @staticmethod
    def _add_color_to_emit_ansi(emit):
        """
        (NON-WINDOWS)
        Takes in Logging.StreamHandler.emit and insert coloring to them
        :param emit: Logging.StreamHandler.emit object
        :return : colored Logging.StreamHandler.emit object
        """

        # add methods we need to the class
        def new_emit(*args):
            levelno = args[1].levelno
            if levelno >= 50:
                color = '\x1b[31m'  # red
            elif levelno >= 40:
                color = '\x1b[31m'  # red
            elif levelno >= 30:
                color = '\x1b[33m'  # yellow
            elif levelno >= 20:
                color = '\x1b[32m'  # green
            elif levelno >= 10:
                color = '\x1b[35m'  # pink
            else:
                color = '\x1b[0m'  # normal

            args[1].msg = color + args[1].msg + '\x1b[0m'  # normal
            # print "after"
            return emit(*args)

        return new_emit
