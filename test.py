__author__ = 'claude'

import unittest
import sha1
import peer
import hashlib
import random
import os
from mylogging import Logging
import testHelper
from kademlia.network import Server


class TestSaymeando(unittest.TestCase):

    helper = testHelper.TestHelper()
    logging = Logging()
    hash = sha1.SHA1(logging)
    node = peer.Peer()

    def test_sha1(self):
        self.logging.setLogId(self.helper.getNewLogId())
        node_id = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
        text = "The quick brown fox jumps over the lazy dog"
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(text))

    def test_sha1_empty(self):
        self.logging.setLogId(self.helper.getNewLogId())
        node_id = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        text = ""
        self.assertEqual(node_id, self.hash.calcNodeID_Sha1(text))

    def test_distance(self):
        self.logging.setLogId(self.helper.getNewLogId())
        self.assertEqual(self.hash.calcDist(self.helper.getRandNodeId2(), self.helper.getRandNodeId1()),
                         self.hash.calcDist(self.helper.getRandNodeId1(), self.helper.getRandNodeId2()))

    def test_gettingTorrent(self):
        self.logging.setLogId(self.helper.getNewLogId())
        self.assertEqual(self.helper.getTorrentContent(), self.hash.readTorrentFile(self.helper.getTorrentFile()))

    def test_metadata(self):
        self.logging.setLogId(self.helper.getNewLogId())
        torrent = self.hash.readTorrentFile(self.helper.getTorrentFile())
        self.assertEqual(self.helper.getMetaData(), self.hash.getMetaData(torrent))

    def test_createInfoHash(self):
        self.logging.setLogId(self.helper.getNewLogId())
        self.assertEqual(self.helper.getInfoHash(), self.hash.createInfoHashFrom(self.helper.getMetaData()))

    def test_createMagnetLink(self):
        self.logging.setLogId(self.helper.getNewLogId())
        self.assertEqual(self.helper.getMagnetLink(), self.hash.createMagnetLinkFrom(self.helper.getInfoHash()))

    def test_createServer(self):
        self.logging.setLogId(self.helper.getNewLogId())
        kademlia_server = self.hash.createServer()
        self.assertEqual(type(kademlia_server), Server)

    def test_setNodeId(self):
        self.logging.setLogId(self.helper.getNewLogId())
        self.node.set_NodeId(self.helper.getInfoHash())
        self.assertEqual(self.helper.getInfoHash(), self.node.get_NodeId())

    def test_gettingTorrent_error(self):
        self.logging.setLogId(self.helper.getNewLogId())
        self.assertEqual(None, self.hash.readTorrentFile(self.helper.getNotExistingFile()))


if __name__ == "__main__":
    unittest.main()


