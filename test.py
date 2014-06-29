__author__ = 'claude'

import unittest
import sha1
import peer
import testHelper
from kademlia.network import Server
from log import LogMsg


class TestSaymeando(unittest.TestCase):

    th = testHelper.TestHelper()
    hash = sha1.SHA1()
    node = peer.Peer()

    def setUp(self):
        self.hash.logging.setLogId(self.th.getNewLogId())
        self.hash.logging.separator()

    def test_sha1(self):
        node_id = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
        text = "The quick brown fox jumps over the lazy dog"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(text))
        self.hash.logging.check(self, ('INFO', LogMsg.RETURNING_SHA1_HASH))

    def test_sha1_empty(self):
        node_id = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(""))

    def test_distance(self):
        self.assertEqual(self.hash.calcDist(self.th.getId2(), self.th.getId1()),
                         self.hash.calcDist(self.th.getId1(), self.th.getId2()))

    def test_gettingTorrent(self):
        self.assertEqual(self.th.getTorCont(), self.hash.readTor(self.th.getTor()))

    def test_metadata(self):
        torrent = self.hash.readTor(self.th.getTor())
        self.assertEqual(self.th.getMetaD(), self.hash.getMetaD(torrent))

    def test_createInfoHash(self):
        self.assertEqual(self.th.getIH(), self.hash.createIHFrom(self.th.getMetaD()))

    def test_createMagnetLink(self):
        self.assertEqual(self.th.getML(), self.hash.createMLFrom(self.th.getIH()))

    def test_createServer(self):
        self.assertEqual(type(self.hash.createServer()), Server)

    def test_setNodeId(self):
        self.node.set_NodeId(self.th.getIH())
        self.assertEqual(self.th.getIH(), self.node.get_NodeId())

    def test_gettingTorrent_error(self):
        self.assertEqual(None, self.hash.readTor(self.th.getNonExFile()))


if __name__ == "__main__":
    unittest.main()
