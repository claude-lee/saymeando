__author__ = 'claude'

import unittest
import sha1
import peer
from log import Logging
from log import log_dec
import testHelper
from kademlia.network import Server


class TestSaymeando(unittest.TestCase):

    th = testHelper.TestHelper()
    logging = Logging()
    hash = sha1.SHA1(logging)
    node = peer.Peer()

    @log_dec
    def test_sha1(self):
        node_id = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
        text = "The quick brown fox jumps over the lazy dog"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(text))

    @log_dec
    def test_sha1_empty(self):
        node_id = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(""))

    @log_dec
    def test_distance(self):
        self.assertEqual(self.hash.calcDist(self.th.getId2(), self.th.getId1()),
                         self.hash.calcDist(self.th.getId1(), self.th.getId2()))

    @log_dec
    def test_gettingTorrent(self):
        self.assertEqual(self.th.getTorCont(), self.hash.readTor(self.th.getTor()))

    @log_dec
    def test_metadata(self):
        torrent = self.hash.readTor(self.th.getTor())
        self.assertEqual(self.th.getMetaD(), self.hash.getMetaD(torrent))

    @log_dec
    def test_createInfoHash(self):
        self.assertEqual(self.th.getIH(), self.hash.createIHFrom(self.th.getMetaD()))

    @log_dec
    def test_createMagnetLink(self):
        self.assertEqual(self.th.getML(), self.hash.createMLFrom(self.th.getIH()))

    @log_dec
    def test_createServer(self):
        self.assertEqual(type(self.hash.createServer()), Server)

    @log_dec
    def test_setNodeId(self):
        self.node.set_NodeId(self.th.getIH())
        self.assertEqual(self.th.getIH(), self.node.get_NodeId())

    @log_dec
    def test_gettingTorrent_error(self):
        self.assertEqual(None, self.hash.readTor(self.th.getNonExFile()))


if __name__ == "__main__":
    unittest.main()
