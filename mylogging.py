__author__ = 'claude'

import hashlib
from twisted.python import log
import os


class Mylogging(log.LogPublisher):


    def __init__(self):
        log.LogPublisher.__init__(self)
        self.cwdir = os.path.dirname(os.path.abspath(__file__))

    def start(self):
        log.startLogging(open(self.cwdir + "/file.log", 'w'))