__author__ = 'claude'

import unittest
import sha1
import peer
import testHelper
from kademlia.network import Server
from log import LogMsg
from testHelper import log_dec
from testHelper import dec_all


@dec_all(log_dec)
class TestSaymeando(unittest.TestCase):

    th = testHelper.TestHelper()
    hash = sha1.SHA1()
    node = peer.Peer()

    def test_sha1(self):
        node_id = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
        text = "The quick brown fox jumps over the lazy dog"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(text))

    def test_1_logging_in_file(self):
        text = "The quick brown fox jumps over the lazy dog"
        self.hash.calcNodeID_Sha1(text)
        log_file = open(self.hash.logging.cwdir + "/" + self.hash.logging.log_file)
        log_file.readline()  # 2014-07-17 12:27:41+0200 [-] Log opened.
        log_file.readline()  #
        log_file.readline()  # #--test_1_logging_in_file------------------#
        line = log_file.readline()[0:-1]
        self.assertEqual(line[-len(LogMsg.RETURNING_SHA1_HASH):], LogMsg.RETURNING_SHA1_HASH)

    def test_sha1_calculation_is_logged(self):
        text = "The quick brown fox jumps over the lazy dog"
        self.hash.calcNodeID_Sha1(text)
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
        self.node.setNodeId(self.th.getIH())
        self.assertEqual(self.th.getIH(), self.node.getNodeId())

    def test_gettingTorrent_error(self):
        self.assertEqual(None, self.hash.readTor(self.th.getNonExFile()))


if __name__ == "__main__":
    unittest.main()
