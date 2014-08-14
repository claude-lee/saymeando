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
        self.th.check(self, ('INFO', [LogMsg.RETURNING_SHA1_HASH]), self.hash.logging.getCachedMsg())

    def test_sha1_empty(self):
        node_id = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(""))

    def test_sha1_empty_is_logged(self):
        self.hash.calcNodeID_Sha1("")
        self.th.check(self, ('INFO', [LogMsg.RETURNING_SHA1_HASH]), self.hash.logging.getCachedMsg())

    def test_distance(self):
        self.assertEqual(self.hash.calcDist(self.th.getId2(), self.th.getId1()),
                         self.hash.calcDist(self.th.getId1(), self.th.getId2()))

    def test_distance_is_logged(self):
        self.hash.calcDist(self.th.getId2(), self.th.getId1())
        self.hash.calcDist(self.th.getId1(), self.th.getId2())
        log_msg_list = [LogMsg.RETURNING_PEER_DISTANCE]
        log_msg_list.append(LogMsg.RETURNING_PEER_DISTANCE)
        self.th.check(self, ('INFO', log_msg_list), self.hash.logging.getCachedMsg())

    def test_gettingTorrent(self):
        self.assertEqual(self.th.getTorCont(), self.hash.readTor(self.th.getTor()))

    def test_gettingTorrent_is_logged(self):
        self.hash.readTor(self.th.getTor())
        self.th.check(self, ('INFO', [LogMsg.OPENING_TORRENT_FILE]), self.hash.logging.getCachedMsg())

    def test_metadata(self):
        torrent = self.hash.readTor(self.th.getTor())
        self.assertEqual(self.th.getMetaD(), self.hash.getMetaD(torrent))

    def test_metadata_is_logged(self):
        torrent = self.hash.readTor(self.th.getTor())
        self.hash.getMetaD(torrent)
        log_msg_list = [LogMsg.OPENING_TORRENT_FILE]
        log_msg_list.append(LogMsg.CREATING_META_DATA_FROM_TORRENT)
        self.th.check(self, ('INFO', log_msg_list), self.hash.logging.getCachedMsg())

    def test_createInfoHash(self):
        self.assertEqual(self.th.getIH(), self.hash.createIHFrom(self.th.getMetaD()))

    def test_createInfoHash_is_logged(self):
        self.hash.createIHFrom(self.th.getMetaD())
        log_msg_list = [LogMsg.CREATING_INFO_HASH_FROM_META_DATA]
        log_msg_list.append(LogMsg.RETURNING_SHA1_HASH)
        self.th.check(self, ('INFO', log_msg_list), self.hash.logging.getCachedMsg())

    def test_createMagnetLink(self):
        self.assertEqual(self.th.getML(), self.hash.createMLFrom(self.th.getIH()))

    def test_createMagnetLink_is_logged(self):
        self.hash.createMLFrom(self.th.getIH())
        self.th.check(self, ('INFO', [LogMsg.CREATING_MAGNET_LINK_FROM_INFO_HASH]), self.hash.logging.getCachedMsg())

    def test_createServer(self):
        self.assertEqual(type(self.hash.createServer()), Server)

    def test_createServer_is_logged(self):
        self.hash.createServer()
        self.th.check(self, ('INFO', [LogMsg.CREATING_KADEMLIA_SERVER]), self.hash.logging.getCachedMsg())

    def test_setNodeId(self):
        self.node.setNodeId(self.th.getIH())
        self.assertEqual(self.th.getIH(), self.node.getNodeId())

    def test_gettingTorrent_error(self):
        self.assertEqual(None, self.hash.readTor(self.th.getNonExFile()))

    def test_gettingTorrent_error_is_logged(self):
        self.hash.readTor(self.th.getNonExFile())
        self.th.check(self, ('ERROR', [LogMsg.ERROR_TORRENT_FILE_DOESNT_EXIST]), self.hash.logging.getCachedMsg())


if __name__ == "__main__":
    unittest.main()
