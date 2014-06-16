__author__ = 'claude'

import hashlib
from twisted.python import log
import os
import bencode
from kademlia.network import Server

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


    def readTorrentFile(self, torrent_location):
        return open(torrent_location, 'r').read()

    def getMetaData(self, torrent):
        return bencode.bdecode(torrent)

    def createInfoHashFrom(self, meta_data):
        hash_contents = bencode.bencode(meta_data['info'])
        return self.calcNodeID_Sha1(hash_contents)

    def createMagnetLinkFrom(self, info_hash):
        return 'magnet:?xt=urn:btih:'+info_hash

    def createServer(self):
        kademlia_server = Server()
        return kademlia_server