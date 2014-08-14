__author__ = 'claude'

from twisted.python import log
import os


class LogMsg():

    RETURNING_SHA1_HASH = "RETURNING torrent SHA1 hash"
    RETURNING_PEER_DISTANCE = "RETURNING peer distance"
    OPENING_TORRENT_FILE = "OPENING torrent file"
    CREATING_META_DATA_FROM_TORRENT = "CREATING metadata from torrent"
    CREATING_INFO_HASH_FROM_META_DATA = "CREATING info hash from meta data"
    CREATING_MAGNET_LINK_FROM_INFO_HASH = "CREATING magnet link from info hash"
    CREATING_KADEMLIA_SERVER = "CREATING kademlia server"
    ERROR_TORRENT_FILE_DOESNT_EXIST = "ERROR: torrent file doesn't exist. "


class Logging(log.LogPublisher):

    def __init__(self):
        log.LogPublisher.__init__(self)
        self.log_id = 0
        self.cwdir = os.path.dirname(os.path.abspath(__file__))
        self.log_file = "saymeando.log"
        log.startLogging(open(self.cwdir + "/" + self.log_file, 'w'))
        self.cached_msg = [0]
        self.section = ''

    def msg(self, text):
        log.msg(self.section + ' >> [' + str(self.log_id) + '] ' + text)
        if self.cached_msg[0] is not self.log_id:
            self.cached_msg = [self.log_id, text]
        else:
            self.cached_msg.append(text)

    def separator(self, text):
        log.msg("")
        log.msg("--" + text + "------------------")

    def setLogId(self, log_id):
        self.log_id = log_id

    def getCachedMsg(self):
        return self.cached_msg

    def setSection(self, sec):
        self.section = sec
