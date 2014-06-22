__author__ = 'claude'

import os
import hashlib
import random


class TestHelper():

    def __init__(self):
        self.logId = 0
        self.not_existing_file = os.path.dirname(os.path.abspath(__file__)) + '/does/not/exist'
        self.torrent_file = os.path.dirname(os.path.abspath(__file__)) + '/sample/sample.torrent'
        self.torrent_content = 'd8:announce35:udp://tracker.openbittorrent.com:8013:creation datei1327049827e4:infod6:lengthi20e4:name10:sample.txt12:piece lengthi65536e6:pieces20:\\\xc5\xe6R\xbe\r\xe6\xf2x\x05\xb3\x04d\xff\x9b\x00\xf4\x89\xf0\xc97:privatei1eee'
        self.meta_data = {'creation date': 1327049827, 'announce': 'udp://tracker.openbittorrent.com:80', 'info': {'length': 20, 'piece length': 65536, 'name': 'sample.txt', 'private': 1, 'pieces': '\\\xc5\xe6R\xbe\r\xe6\xf2x\x05\xb3\x04d\xff\x9b\x00\xf4\x89\xf0\xc9'}}
        self.rand_node_id_1 = hashlib.sha1(str(random.getrandbits(255)))
        self.rand_node_id_2 = hashlib.sha1(str(random.getrandbits(255)))
        self.info_hash = 'd0d14c926e6e99761a2fdcff27b403d96376eff6'
        self.magnet_link = 'magnet:?xt=urn:btih:d0d14c926e6e99761a2fdcff27b403d96376eff6'

    def getLogId(self):
        return self.logId

    def getNewLogId(self):
        self.logId += 1
        return self.logId

    def getNotExistingFile(self):
        return self.not_existing_file

    def getTorrentFile(self):
        return self.torrent_file

    def getTorrentContent(self):
        return self.torrent_content

    def getMetaData(self):
        return self.meta_data

    def getRandNodeId1(self):
        return self.rand_node_id_1

    def getRandNodeId2(self):
        return self.rand_node_id_2

    def getInfoHash(self):
        return self.info_hash

    def getMagnetLink(self):
        return self.magnet_link
