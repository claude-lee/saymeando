__author__ = 'claude'

import unittest
import sha1
import hashlib
import random
import os

class TestSaymeando(unittest.TestCase):

    def test_sha1(self):
        node_id = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
        text = "The quick brown fox jumps over the lazy dog"
        self.assertEqual(node_id, sha1.SHA1().calcNodeID_Sha1(text))

    def test_sha1_empty(self):
        node_id = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        text = ""
        self.assertEqual(node_id, sha1.SHA1().calcNodeID_Sha1(text))

    def test_distance(self):
        node_id_1 = hashlib.sha1(str(random.getrandbits(255)))
        node_id_2 = hashlib.sha1(str(random.getrandbits(255)))
        self.assertEqual(sha1.SHA1().calcDistance(node_id_2, node_id_1)
                         ,sha1.SHA1().calcDistance(node_id_1, node_id_2))

    def test_gettingTorrent(self):
        torrent_location = os.path.dirname(os.path.abspath(__file__))+'/sample/sample.torrent'
        torrent_content = 'd8:announce35:udp://tracker.openbittorrent.com:8013:creation datei1327049827e4:infod6:lengthi20e4:name10:sample.txt12:piece lengthi65536e6:pieces20:\\\xc5\xe6R\xbe\r\xe6\xf2x\x05\xb3\x04d\xff\x9b\x00\xf4\x89\xf0\xc97:privatei1eee'
        self.assertEqual(torrent_content, sha1.SHA1().readTorrentFile(torrent_location))

    def test_import_bencode(self):
        pass

    def test_metadata(self):
        torrent_location = os.path.dirname(os.path.abspath(__file__))+'/sample/sample.torrent'
        torrent = sha1.SHA1().readTorrentFile(torrent_location)
        meta_data = {'creation date': 1327049827, 'announce': 'udp://tracker.openbittorrent.com:80', 'info': {'length': 20, 'piece length': 65536, 'name': 'sample.txt', 'private': 1, 'pieces': '\\\xc5\xe6R\xbe\r\xe6\xf2x\x05\xb3\x04d\xff\x9b\x00\xf4\x89\xf0\xc9'}}
        self.assertEqual(meta_data, sha1.SHA1().getMetaData(torrent))

    def test_createInfoHash(self):
        torrent_location = os.path.dirname(os.path.abspath(__file__))+'/sample/sample.torrent'
        torrent = sha1.SHA1().readTorrentFile(torrent_location)
        meta_data = sha1.SHA1().getMetaData(torrent)
        info_hash = 'd0d14c926e6e99761a2fdcff27b403d96376eff6'
        self.assertEqual(info_hash, sha1.SHA1().createInfoHashFrom(meta_data))

    def test_createMagneLink(self):
        info_hash =  'd0d14c926e6e99761a2fdcff27b403d96376eff6'
        magnet_link = 'magnet:?xt=urn:btih:d0d14c926e6e99761a2fdcff27b403d96376eff6'
        self.assertEqual(magnet_link, sha1.SHA1().createMagnetLinkFrom(info_hash))

    def test_createServer(self):
        kademlia_server = str(sha1.SHA1().createServer())
        pass






    # def testMagnetLink(self):
    #     magnet_link = "magnet:" \
    #                   "?xt=urn:ed2k:31D6CFE0D16AE931B73C59D7E0C089C0" \
    #                   "&xl=0&dn=zero_len.fil" \
    #                   "&xt=urn:bitprint:3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ.LWPNACQDBZRYXW3VHJVCJ64QBZNGHOHHHZWCLNQ" \
    #                   "&xt=urn:md5:D41D8CD98F00B204E9800998ECF8427E"


if __name__ == "__main__":
    unittest.main()
