__author__ = 'claude'

import hashlib
import bencode
from kademlia.network import Server
from log import Logging
from log import LogMsg


class SHA1:

    def __init__(self):
        self.logging = Logging()

    def calcNodeID_Sha1(self, text):
        self.logging.setSection('discovery')
        self.logging.msg(LogMsg.RETURNING_SHA1_HASH)
        return hashlib.sha1(text).hexdigest()

    def calcDist(self, node_id_1, node_id_2):
        self.logging.msg(LogMsg.RETURNING_PEER_DISTANCE)
        return long(node_id_1.hexdigest(), 16) ^ long(node_id_2.hexdigest(), 16)

    def readTor(self, torrent_location):
        read_file = None
        try:
            read_file = open(torrent_location, 'r').read()
            self.logging.msg(LogMsg.OPENING_TORRENT_FILE)
        except IOError as e:
            self.logging.msg(LogMsg.ERROR_TORRENT_FILE_DOESNT_EXIST + str(e))
        return read_file

    def getMetaD(self, torrent):
        self.logging.msg(LogMsg.CREATING_META_DATA_FROM_TORRENT)
        return bencode.bdecode(torrent)

    def createIHFrom(self, meta_data):
        hash_contents = bencode.bencode(meta_data['info'])
        self.logging.msg(LogMsg.CREATING_INFO_HASH_FROM_META_DATA)
        return self.calcNodeID_Sha1(hash_contents)

    def createMLFrom(self, info_hash):
        self.logging.setSection('calculation')
        self.logging.msg(LogMsg.CREATING_MAGNET_LINK_FROM_INFO_HASH)
        return 'magnet:?xt=urn:btih:' + info_hash

    def createServer(self):
        self.logging.msg(LogMsg.CREATING_KADEMLIA_SERVER)
        kademlia_server = Server()
        return kademlia_server
