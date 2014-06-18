__author__ = 'claude'

import hashlib
from twisted.python import log
import os


class Logging(log.LogPublisher):


    def __init__(self):
        log.LogPublisher.__init__(self)
        self.cwdir = os.path.dirname(os.path.abspath(__file__))
        log.startLogging(open(self.cwdir + "/file.log", 'w'))
        self.log_id = 0


    def msg(self, text):
        log.msg('[' + str(self.log_id) + '] ' + text)

    def setLogId(self, log_id):
        self.log_id = log_id