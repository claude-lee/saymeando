__author__ = 'claude'


class Peer(object):

    def __init__(self, node_id=0):
        self.node_id = node_id

    def setNodeId(self, node_id):
        self.node_id = node_id

    def getNodeId(self):
        return self.node_id
