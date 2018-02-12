# MIT License
#
# Copyright 2017-2018 Dmitry Vodopyanov, dmitry.vodopyanov@gmail.com
# Copyright 2017-2018 Artem Kashkanov, radiolokn@gmail.com
# Copyright 2017-2018 Sergey Shtin, sergey.shtin@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import logging
import logging.config
import inspect
import os
import types


def init_logger(logdir=None):
    if logdir is None:
        logdir = 'logs'

    os.makedirs(logdir, exist_ok=True)

    logger_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)-8s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'custom': {
                '()': 'src.logger.CustomFormatter',
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'custom',
            },
            'summary': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(logdir, "summary.log"),
                'encoding': 'utf-8',
                'formatter': 'custom',
                'mode': 'w',
            },
        },
        'loggers': {
            'fr3onn': {
                'handlers': ['summary', 'console'],
                'level': 'DEBUG',
                'propagate': True
            },
        }
    }

    logging.config.dictConfig(logger_config)

    # hack for indentation in logs
    decorate_logger(logging.Logger, logging.Logger._log)

    fix_logger_for_linux_cmd()


def decorate_logger(logger, func):
    def my_decorator(self, level, msg, args, exc_info=None, extra=None):
        msg = ' ' * self._indent + str(msg)
        func(self, level, msg, args, exc_info, extra)

    def increase_indent(self, inc=2):
        self._indent += inc

    def decrease_indent(self, inc=2):
        self._indent -= inc

    logger._indent = 0
    logger.increase_indent = increase_indent
    logger.decrease_indent = decrease_indent
    logger._log = my_decorator
    logger_custom = logging.getLogger('fr3onn')
    logger._main_handlers = logger_custom.handlers[:]


def fix_logger_for_linux_cmd():
    def write(self, txt):
        self.debug("\n%s\n" % txt.decode("utf-8", 'ignore').
                   replace("\x1b[2J\x1b[1;1H", '').
                   replace("\x1b[7m", '').
                   replace("\x1b[27m", ''))

    logger = logging.getLogger('fr3onn')
    logger.write = types.MethodType(write, logger)
    logger.flush = types.MethodType(lambda x: None, logger)


def switch_to_custom(name, logdir="logs"):
    logger = logging.getLogger('fr3onn')

    remove_summary()
    remove_customs()

    handler = UniqueFileHandler(name + '.log', logdir)
    logger.addHandler(handler)


def add_custom(name, logdir="logs"):
    logger = logging.getLogger('fr3onn')

    handler = UniqueFileHandler(name + '.log', logdir)
    logger.addHandler(handler)


def add_summary():
    logger = logging.getLogger('fr3onn')

    for handler in logger._main_handlers:
        logger.addHandler(handler)


def remove_summary():
    logger = logging.getLogger('fr3onn')

    handlers = logger.handlers[:]
    for handler in handlers:
        if (handler._name == 'summary') or (handler._name == 'console'):
            logger.removeHandler(handler)


def remove_customs():
    logger = logging.getLogger('fr3onn')

    handlers = logger.handlers[:]
    for handler in handlers:
        if isinstance(handler, UniqueFileHandler):
            logger.removeHandler(handler)


def switch_to_summary():
    remove_customs()
    add_summary()


class UniqueFileHandler(object):
    """ Handler that creates log file into custom logging directory """

    def __init__(self, filename, dir_=os.getcwd(), **kwargs):
        kwargs['filename'] = os.path.join(dir_, filename)
        kwargs['mode'] = 'w'

        os.makedirs(dir_, exist_ok=True)

        self._handler = logging.FileHandler(**kwargs)
        self._handler.setFormatter(CustomFormatter())
        self._handler.setLevel(logging.DEBUG)

    def __getattr__(self, n):
        if hasattr(self._handler, n):
            return getattr(self._handler, n)
        raise AttributeError


class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.baseline = len(inspect.stack())

    def format(self, record):
        record.indent = ''
        record.message = record.getMessage().split('\n')
        s = ""
        for i in record.message:
            if len(i.strip()) > 0:
                s += "[%s] %s %s %s\n" % (self.formatTime(record, '%Y-%m-%d %H:%M:%S'),
                                          record.levelname.ljust(8),
                                          record.indent, i)
        s = s[:-1]
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                exc_text = self.formatException(record.exc_info)
                record.exc_text = self.format_exception_better(exc_text)
        if record.exc_text:
            if s[-1:] != "\n":
                s += "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s += "\n"
            s = s + self.formatStack(record.stack_info)

        return s

    def format_exception_better(self, text):
        t = text.split('\n')
        s = ""
        for i in t:
            s += " " * 10 + "| %s\n" % i
        return s[:-1]
