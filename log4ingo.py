#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import logging
import logging.handlers

__author__ = 'real'
__email__ = 'real@the-real.org'
__license__ = 'GPL3'
__copyright__ = '(c) by Robin Wittler <real@the-real.org>'
__version__ = '0.1.0'

SYSLOG_DEFAULT = '/dev/log'
STDOUT_DEFAULT = '/dev/stdout'

BASE_FORMAT_SYSLOG = (
    '%(name)s.%(funcName)s[PID: %(process)d | lineno: %(lineno)d] ' +
    '%(levelname)s: %(message)s'
)

BASE_FORMAT_STDOUT = '%(asctime)s ' + BASE_FORMAT_SYSLOG

logger = logging.getLogger(__name__)

class BaseObject(object):
    def __new__(cls, *targs, **kwargs):
        _cls = object.__new__(cls, *targs, **kwargs)
        setattr(
            _cls,
            'logger',
            logging.getLogger(
                '%s.%s'
                %(
                    cls.__module__,
                    _cls.__class__.__name__
                )
            )
        )
        return _cls

    def __getattribute__(self, name):
        myname = object.__getattribute__(self, '__class__').__name__

        logger = logging.getLogger(
            '%s.%s'
            %(
                __name__,
                myname
            )
        )
        logger.debug(
            'Called to get attribute with name: %s',
            name
        )

        attribute = object.__getattribute__(self, name)
        if callable(attribute):
            _callable = attribute
            def _logwrapper(*targs, **kwargs):
                _logger = logging.getLogger(
                    '%s.%s.%s'
                    %(
                        __name__,
                        myname,
                        name
                    )
                )
                _logger.debug(
                    'Called to exec with targs: %s and kwargs: %s'
                    %(targs, kwargs)
                )
                result = _callable(*targs, **kwargs)
                _logger.debug(
                    'return with result: %s', result
                )
                return result

            logger.debug(
                'Wrapping callabel %s to add logging',
                attribute
            )
            attribute = _logwrapper
        else:
            logger.debug(
                '%s is: %s',
                name,
                type(attribute)
            )

        return attribute

    def __setattr__(self, key, value):
        myname = object.__getattribute__(self, '__class__').__name__

        logger = logging.getLogger(
            '%s.%s'
            %(
                __name__,
                myname
            )
        )
        logger.debug(
            'Called to set attribute with name %s to value %s ',
            key,
            value
        )

        attribute = getattr(self, key, None)
        if attribute is None:
            logger.debug('Attribute %s is a new Attribute.', key)

        logger.debug(
            'Changing Attribute %s from %s (%s) to %s (%s)',
            key,
            attribute,
            type(attribute),
            value,
            type(value),
        )
        
        return object.__setattr__(self, key, value)


class LoggingBase(BaseObject):
    def __init__(self, config=None, level=logging.DEBUG, syslog=False):
        self.config = config
        self.level = level
        self.syslog = syslog

        if self.config is not None:
            self.fileConfig(self.config)
        else:
            self.basicConfig()

    def basicConfig(self, *targs, **kwargs):
        map(
            lambda x: self.root_logger.removeHandler(x),
            self.root_logger.handlers
        )

        stdout = logging.StreamHandler(stream=sys.stdout)
        stdout.setLevel(logging.DEBUG)
        stdout.setFormatter(
            logging.Formatter(BASE_FORMAT_STDOUT)
        )

        if self.syslog is not False:
            if isinstance(self.syslog, (tuple, list)):
                address = self.syslog
            elif isinstance(self.syslog, str):
                address = self.syslog
            elif self.syslog is True and 'linux' in sys.platform:
                address = '/dev/log'
            else:
                address = SYSLOG_DEFAULT

            syslog_handler = logging.handlers.SysLogHandler(
                address=address, facility=1, socktype=2
            )
            syslog_handler.setLevel(logging.DEBUG)
            syslog_handler.setFormatter(
                logging.Formatter(BASE_FORMAT_SYSLOG)
            )
            self.root_logger.addHandler(syslog_handler)
        self.root_logger.addHandler(stdout)
        self.root_logger.setLevel(self.level)
        logging.basicConfig(
            format=BASE_FORMAT_STDOUT,
            level=self.level,
            filename=STDOUT_DEFAULT
        )
        self.logger.info('LoggingBase initialised.')
        return True

    def fileConfig(self, path, *targs, **kwargs):
        return logging.config.fileConfig(path)

    @property
    def root_logger(self):
        return logging.getLogger('')

    @property
    def logger_names(self):
        return self.root_logger.manager.loggerDict.keys()

    @property
    def iterLoggers(self):
        return self.root_logger.manager.loggerDict.iteritems

    def getLogger(self, name):
        return logging.getLogger(name)

    def setLevel(self, level, regex=None):
        if regex is None:
            self.logger.debug(
                'Setting level of root logger to %s',
                level
            )
            return self.root_logger.setLevel(level)

        self.logger.debug(
            'Entering extended setLevel mode.'
        )
        cregex = re.compile(regex)
        for name, logger in self.iterLoggers():
            try:
                match = cregex.match(name)
                if match is not None:
                    self.logger.debug(
                        'Setting level of logger %s to %s',
                        name,
                        level
                    )
                    logger.setLevel(level)
                else:
                    self.logger.debug(
                        'Logger %s does not match regex %s',
                        name,
                        regex
                    )
            except Exception, error:
                self.logger.exception(error)
                self.logger.warning('Continue after error ...')
                continue
        self.logger.debug('Leaving extended setLevel mode.')
        return None

    def setInverseLevel(self, level, regex):
        cregex = re.compile(regex)
        for name, logger in self.iterLoggers():
            try:
                match = cregex.match(name)
                if match is None:
                    self.logger.debug(
                        'Setting level of logger %s to %s',
                        name,
                        level
                    )
                else:
                    self.logger.debug(
                        'Found target logger %s for regex %s. Continue ...',
                        name,
                        regex
                    )
                    continue
            except Exception, error:
                self.logger.exception(error)
                self.logger.warning('Continue after error ...')
                continue
        return None

if __name__ == '__main__':
    pass