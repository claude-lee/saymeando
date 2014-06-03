__author__ = 'claude'

import unittest
import sha1

class TestSaymeando(unittest.TestCase):

    def test1(self):
        text_1 = ""
        text_2 = "2jmj7l5rSw0yVb/vlWAYkK/YBwk="
        self.assertEqual(text_2, sha1.SHA1().calc_SHA1_value_base64(text_1))

    # def test2(self):
    #     text_1 = ""
    #     text_2 = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    #     self.assertEqual(text_2, sha1.SHA1().calc_SHA1_value_hex(text_1))

    def test3(self):
        text_1 = "The quick brown fox jumps over the lazy dog"
        text_2 = "L9ThxnotKPzthJ7hu3bnORuT6xI="
        self.assertEqual(text_2, sha1.SHA1().calc_SHA1_value_base64(text_1))

    # def test4(self):
    #     text_1 = "The quick brown fox jumps over the lazy dog"
    #     text_2 = "2fd4e1c67a2d28fced849ee1bb76e7391b93eb12"
    #     self.assertEqual(text_2, sha1.SHA1().calc_SHA1_value_hex(text_1))



if __name__ == "__main__":
    unittest.main()
