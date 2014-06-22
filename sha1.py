__author__ = 'claude'

import hashlib
import bencode
from kademlia.network import Server
from mylogging import Logging


class SHA1:

    def __init__(self, logging):
        self.logging = logging

    def calcNodeID_Sha1(self, text):
        self.logging.msg("RETURNING torrent SHA1 hash")
        return hashlib.sha1(text).hexdigest()

    def calcDist(self, node_id_1, node_id_2):
        self.logging.msg("RETURNING peer distance")
        return long(node_id_1.hexdigest(), 16) ^ long(node_id_2.hexdigest(), 16)

    def readTorrentFile(self, torrent_location):
        read_file = None
        try:
            read_file = open(torrent_location, 'r').read()
            self.logging.msg("OPENING torrent file")
        except IOError as e:
            self.logging.msg("ERROR: torrent file doesn't exist. " + str(e))
        return read_file

    def getMetaData(self, torrent):
        self.logging.msg("CREATING metadata from torrent")
        return bencode.bdecode(torrent)

    def createInfoHashFrom(self, meta_data):
        hash_contents = bencode.bencode(meta_data['info'])
        self.logging.msg("CREATING info hash from meta data")
        return self.calcNodeID_Sha1(hash_contents)

    def createMagnetLinkFrom(self, info_hash):
        self.logging.msg("CREATING magnet link from info hash")
        return 'magnet:?xt=urn:btih:' + info_hash

    def createServer(self):
        self.logging.msg("CREATING kademlia server")
        kademlia_server = Server()
        return kademlia_server
