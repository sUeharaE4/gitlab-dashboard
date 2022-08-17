"""Provice logger."""
import inspect
import logging
import logging.handlers
import os
import sys
import traceback
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Union

from . import Const

loggers: dict[str, Any] = {}


class CustomLogger(logging.Logger):
    """Force the closing of file handlers and the creation of console handlers."""

    def __init__(self, name: str, level: int = logging.NOTSET) -> None:
        """Simply exec init of logging.Logger class."""
        super().__init__(name, level)

    def close_file_handler(self) -> None:
        """Close all file handlers."""
        for handler in self.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

    def set_stream_when_none(self) -> None:
        """Set stream handler if this logger hasn't it."""
        st_handlers = [h for h in self.handlers if isinstance(h, logging.StreamHandler) and h.stream is None]
        for handler in st_handlers:
            # FileHandler is subclass of StreamHandler so check before set stream stdout
            if isinstance(handler, logging.FileHandler):
                continue
            handler.stream = sys.stdout

    def __find_caller(self, wrapper_depth: int) -> dict:
        def make_dict(filename, funcname, lineno) -> dict:
            return {
                "real_filename": self.split_filepath(filename),
                "real_funcName": funcname,
                "real_lineno": lineno,
            }

        # stack0: this function, 1: log function, 2: context manager, 3: contextlib
        target_info = inspect.stack()[4 + wrapper_depth]
        return make_dict(target_info.filename, target_info.function, target_info.lineno)

    @contextmanager
    def logging_context(self, wrapper_depth: int, kwargs_dict: dict):
        """Provide common processing for logging.

        Parameters
        ----------
        wrapper_depth
            set depth of wrapping if caller wrapped.
        kwargs_dict
            set **kwargs if need.

        Yields
        ------
        dict
            preprocessed extra kwargs for logging function.
        """
        try:
            self.set_stream_when_none()
            if "extra" not in kwargs_dict:
                kwargs_dict["extra"] = self.__find_caller(wrapper_depth)
            yield kwargs_dict
            self.close_file_handler()
        except Exception as e:
            trace_str = traceback.format_exception_only(type(e), e)
            print(f"exception raised when logging: {trace_str}")
        finally:
            pass

    def debug(self, msg: str, wrapper_depth: int = 0, *args, **kwargs) -> None:
        """Output debug message.

        Parameters
        ----------
        msg
            massage for logging.
        wrapper_depth
            set wrapper depth when caller wrapped, by default 0
        """
        with self.logging_context(wrapper_depth, kwargs) as logging_kwargs:
            super().debug(msg, *args, **logging_kwargs)

    def info(self, msg: str, wrapper_depth: int = 0, *args, **kwargs) -> None:
        """Output info message.

        Parameters
        ----------
        msg
            massage for logging.
        wrapper_depth
            set wrapper depth when caller wrapped, by default 0
        """
        with self.logging_context(wrapper_depth, kwargs) as logging_kwargs:
            super().info(msg, *args, **logging_kwargs)

    def warning(self, msg: str, wrapper_depth: int = 0, *args, **kwargs) -> None:
        """Output warning message.

        Parameters
        ----------
        msg
            massage for logging.
        wrapper_depth
            set wrapper depth when caller wrapped, by default 0
        """
        with self.logging_context(wrapper_depth, kwargs) as logging_kwargs:
            super().warning(msg, *args, **logging_kwargs)

    def error(self, msg: str, wrapper_depth: int = 0, *args, **kwargs) -> None:
        """Output error message.

        Parameters
        ----------
        msg
            massage for logging.
        wrapper_depth
            set wrapper depth when caller wrapped, by default 0
        """
        with self.logging_context(wrapper_depth, kwargs) as logging_kwargs:
            super().error(msg, *args, **logging_kwargs)

    def critical(self, msg: str, wrapper_depth: int = 0, *args, **kwargs) -> None:
        """Output critical message.

        Parameters
        ----------
        msg
            massage for logging.
        wrapper_depth
            set wrapper depth when caller wrapped, by default 0
        """
        with self.logging_context(wrapper_depth, kwargs) as logging_kwargs:
            super().critical(msg, *args, **logging_kwargs)

    @staticmethod
    def split_filepath(filepath: str, split_str: str = None) -> str:
        r"""Drop part of filepath to make short massage.

        Parameters
        ----------
        filepath
            path of function definition python file.
        split_str
            drop target strings. need not / or \, if None use str(Const.SRC_ROOT)

        Returns
        -------
        str
            Dropped massage.
        """
        if split_str is None:
            split_str = str(Const.SRC_ROOT)
        dropped_path = filepath.split(split_str)[-1]
        return os.path.join(*dropped_path.split(os.sep))


class CustomFilter(logging.Filter):
    """Filter for output information of logging caller."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        """Set caller information."""
        record.real_filename = getattr(record, "real_filename", record.filename)
        record.real_funcName = getattr(record, "real_funcName", record.funcName)
        record.real_lineno = getattr(record, "real_lineno", record.lineno)
        return True


def get_logger(name: str = None, level: int = Const.LOG_LEVEL, log_path: Union[Path, str] = None) -> CustomLogger:
    """Create (or return pre exists) logger.

    Parameters
    ----------
    name
        set logger name if need, by default None
    level
        set log level, by default Const.LOG_LEVEL
    log_path
        set output log file path if need, by default None

    Returns
    -------
    CustomLogger
        Created logger.
    """
    global loggers
    if name is None:
        name = __name__
    pre_def_logger = loggers.get(name)
    if pre_def_logger:
        return pre_def_logger

    log_format = "[%(asctime)s] [%(levelname)s] [%(real_filename)s:%(real_funcName)s:%(real_lineno)s] -> %(message)s"

    logger = CustomLogger(name, level)
    logger.propagate = False
    logger.addFilter(CustomFilter())

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    if log_path:
        log_dir = os.path.dirname(log_path)
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_path, encoding="utf-8", when="MIDNIGHT", backupCount=7
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    logger.setLevel(level)
    loggers[name] = logger
    return logger


def logging_start_end(logger: logging.Logger):
    """Decorate function to logging."""

    def _decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            filename = CustomLogger.split_filepath((inspect.getabsfile(func)))
            current_frame = inspect.currentframe()
            if current_frame and current_frame.f_back:
                lineno = str(current_frame.f_back.f_lineno)
            else:
                lineno = "can not find line number"
            extra = {"real_filename": filename, "real_funcName": func_name, "real_lineno": lineno}
            try:
                logger.debug(f"[START] {func_name}", extra=extra)
                func_result = func(*args, **kwargs)
                logger.debug(f"[END  ] {func_name}", extra=extra)
                return func_result
            except Exception as err:
                logger.error(err, exc_info=True, extra=extra)
                logger.error(f"[FAILED] {func_name}", extra=extra)
                raise err

        return wrapper

    return _decorator
