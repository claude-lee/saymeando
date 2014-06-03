__author__ = 'claude'

import math
import hashlib
from base64 import b64decode, b64encode
#from Crypto.Hash import SHA1
import libtorrent as lt
import time

class SHA1:

    def calc_SHA1_value_base64(self, text):

        return hashlib.sha1(text).digest()

    def calc_SHA1_value_hex(self, text):
        return text


