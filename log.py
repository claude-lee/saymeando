__author__ = 'claude'

from twisted.python import log
import os
from unittest import TestCase


class LogMsg():

    RETURNING_SHA1_HASH = "RETURNING torrent SHA1 hash"


class Logging(log.LogPublisher):

    def __init__(self):
        log.LogPublisher.__init__(self)
        self.log_id = 0
        self.cwdir = os.path.dirname(os.path.abspath(__file__))
        log.startLogging(open(self.cwdir + "/saymeando.log", 'w'))
        self.cached_msg = ()

    def msg(self, text):
        log.msg('[' + str(self.log_id) + '] ' + text)
        self.cached_msg = (self.log_id, text)

    def separator(self):
        log.msg("#------------------------------------------#")

    def setLogId(self, log_id):
        self.log_id = log_id

    def check(self, tc, exp_log):
        exp_level, exp_msg = exp_log
        TestCase.assertEqual(tc, exp_msg, self.cached_msg[1])
