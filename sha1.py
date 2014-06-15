__author__ = 'claude'

import hashlib
from twisted.python import log
import os

class SHA1:

    def calcNodeID_Sha1(self, text):
        cwdir = os.path.dirname(os.path.abspath(__file__))
        log.startLogging(open(cwdir+"/file.log", 'w'))
        log.msg("STARTING")
        log.err("ERROR: Starting failed")

        log.msg("RETURNING torrent SHA1 hash")
        return hashlib.sha1(text).hexdigest()


    def calcDistance(self, node_id_1, node_id_2):

        return long(node_id_1.hexdigest(), 16) ^ long(node_id_2.hexdigest(), 16)


