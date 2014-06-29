__author__ = 'claude'

import hashlib
from twisted.python import log
import os


def log_dec(func):
    def decorator(self):
        self.logging.setLogId(self.helper.getNewLogId())
        return func(self)
    return decorator


class Logging(log.LogPublisher):

    def __init__(self):
        log.LogPublisher.__init__(self)
        self.cwdir = os.path.dirname(os.path.abspath(__file__))
        log.startLogging(open(self.cwdir + "/saymeando.log", 'w'))
        self.log_id = 0

    def msg(self, text):
        log.msg('[' + str(self.log_id) + '] ' + text)

    def setLogId(self, log_id):
        self.log_id = log_id
