__author__ = 'claude'

from twisted.python import log
import os
from unittest import TestCase
import inspect


def log_dec(func, tc_name):
    def decorator(self):
        self.hash.logging.separator(tc_name)
        self.hash.logging.setLogId(self.th.getNewLogId())
        return func(self)
    return decorator


def dec_all(decorator, prefix='test'):
    def dec_class(tc_class):
        for name, m in inspect.getmembers(tc_class, inspect.ismethod):
            if name.startswith(prefix):
                setattr(tc_class, name, decorator(m, name))
        return tc_class
    return dec_class


class LogMsg():

    RETURNING_SHA1_HASH = "RETURNING torrent SHA1 hash"


class Logging(log.LogPublisher):

    def __init__(self):
        log.LogPublisher.__init__(self)
        self.log_id = 0
        self.cwdir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = "saymeando.log"
        log.startLogging(open(self.cwdir + "/" + self.log_file, 'w'))
        self.cached_msg = ()

    def msg(self, text):
        log.msg('[' + str(self.log_id) + '] ' + text)
        self.cached_msg = (self.log_id, text)

    def separator(self, tc_name):
        log.msg("")
        log.msg("#--" + tc_name + "------------------#")

    def setLogId(self, log_id):
        self.log_id = log_id

    def check(self, tc, exp_log):
        exp_level, exp_msg = exp_log
        TestCase.assertEqual(tc, exp_msg, self.cached_msg[1])
