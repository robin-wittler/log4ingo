#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging
import logging.handlers
from baselibs import BaseObject
from baselibs import base_objects_logger_names

__author__ = 'real'
__email__ = '%s@the-real.org' %(__author__)

BASE_FORMAT_SYSLOG = (
    '%(name)s.%(funcName)s[%(process)d] %(levelname)s: %(message)s'
)

BASE_FORMAT_STDOUT = '%(asctime)s ' + BASE_FORMAT_SYSLOG

logger = logging.getLogger(__name__)

class BasicLogging(BaseObject):
    def __init__(self,config=None, level=logging.DEBUG, syslog=None):
        self.config = config
        self.level = level

        logging.basicConfig(
            level=self.level,
            format=BASE_FORMAT_STDOUT,
            filename='/dev/stdout'
        )

        self.root_logger = logging.getLogger('')
        self.syslog = syslog
        if syslog is not None:
            if syslog is True:
                self.syslog = LinuxSyslog()
            self.root_logger.addHandler(self.syslog)
            self.logger.debug('Added syslog handler: %s', self.syslog)

        self.logger.debug('Initialised.')

    def setLevel(self, level):
        self.root_logger.setLevel(level)

    @property
    def handlers(self):
        return self.root_logger.handlers

    @property
    def all_logger_names(self):
        return base_objects_logger_names

    def addHandler(self, handler):
        return self.root_logger.addHandler(handler)

    def getLoggerFromRegex(self, regex):
        self.logger.debug('Getting logger from regex "%s"', regex)
        return map(
            lambda x: x.string,
            filter(
                None,
                map(
                    lambda x: re.match(regex, x),
                    self.all_logger_names.items
                )
            )
        )

    def setLoggerLevelFromRegex(self, level, regex):
        self.logger.debug('Setting Loglevel %s for regex "%s"', level, regex)
        map(
            lambda x: (
                self.logger.debug(
                    'Set Loglevel %s for logger %s.'
                    %(level, x)
                ),
                logging.getLogger(x).setLevel(level),
            ),
            self.getLoggerFromRegex(regex)
        )
        return True

class LinuxSyslog(BaseObject, logging.handlers.SysLogHandler):
    def __init__(self, address='/dev/log', facility=1, socktype=2):
        super(LinuxSyslog, self).__init__(
            address=address,
            facility=facility,
            socktype=socktype
        )
        self.setFormatter(logging.Formatter(BASE_FORMAT_SYSLOG))
        self.logger.debug('Initialised.')

def getLogger(name):
    logger.debug('Getting logger for: %s', name)
    base_objects_logger_names.appendItem(name)
    return logging.getLogger(name)

if __name__ == '__main__':
    pass