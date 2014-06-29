__author__ = 'claude'

from twisted.python import log
import os
import inspect

def log_dec(func):
    def decorator(self):
        self.logging.setLogId(self.th.getNewLogId())
        return func(self)
    return decorator


def dec_all(decorator, prefix='test'):
  def dec_class(tc_class):
    for name, m in inspect.getmembers(tc_class, inspect.ismethod):
      if name.startswith(prefix):
        setattr(tc_class, name, decorator(m))
    return tc_class
  return dec_class


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
