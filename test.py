__author__ = 'claude'

import unittest
import sha1
import peer
from log import Logging
import log
import testHelper
from kademlia.network import Server



class TestSaymeando(unittest.TestCase):

    helper = testHelper.TestHelper()
    logging = Logging()
    hash = sha1.SHA1(logging)
    node = peer.Peer()


    @log.log_dec
    def test_sha1(self):
        node_id = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
        text = "The quick brown fox jumps over the lazy dog"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(text))

    @log.log_dec
    def test_sha1_empty(self):
        node_id = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        text = ""
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(text))

    @log.log_dec
    def test_distance(self):
        self.assertEqual(self.hash.calcDist(self.helper.getRandNodeId2(), self.helper.getRandNodeId1()),
                         self.hash.calcDist(self.helper.getRandNodeId1(), self.helper.getRandNodeId2()))

    @log.log_dec
    def test_gettingTorrent(self):
        self.assertEqual(self.helper.getTorrentContent(), self.hash.readTorrentFile(self.helper.getTorrentFile()))

    @log.log_dec
    def test_metadata(self):
        torrent = self.hash.readTorrentFile(self.helper.getTorrentFile())
        self.assertEqual(self.helper.getMetaData(), self.hash.getMetaData(torrent))

    @log.log_dec
    def test_createInfoHash(self):
        self.assertEqual(self.helper.getInfoHash(), self.hash.createInfoHashFrom(self.helper.getMetaData()))

    @log.log_dec
    def test_createMagnetLink(self):
        self.assertEqual(self.helper.getMagnetLink(), self.hash.createMagnetLinkFrom(self.helper.getInfoHash()))

    @log.log_dec
    def test_createServer(self):
        kademlia_server = self.hash.createServer()
        self.assertEqual(type(kademlia_server), Server)

    @log.log_dec
    def test_setNodeId(self):
        self.node.set_NodeId(self.helper.getInfoHash())
        self.assertEqual(self.helper.getInfoHash(), self.node.get_NodeId())

    @log.log_dec
    def test_gettingTorrent_error(self):
        self.assertEqual(None, self.hash.readTorrentFile(self.helper.getNotExistingFile()))



if __name__ == "__main__":
    unittest.main()


