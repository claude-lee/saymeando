__author__ = 'claude'

import unittest
import sha1
import hashlib
import random

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




    # def testMagnetLink(self):
    #     magnet_link = "magnet:" \
    #                   "?xt=urn:ed2k:31D6CFE0D16AE931B73C59D7E0C089C0" \
    #                   "&xl=0&dn=zero_len.fil" \
    #                   "&xt=urn:bitprint:3I42H3S6NNFQ2MSVX7XZKYAYSCX5QBYJ.LWPNACQDBZRYXW3VHJVCJ64QBZNGHOHHHZWCLNQ" \
    #                   "&xt=urn:md5:D41D8CD98F00B204E9800998ECF8427E"


if __name__ == "__main__":
    unittest.main()
