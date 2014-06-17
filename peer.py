__author__ = 'claude'




class Peer(object):


    def __init__(
    self, node_id=0):
        self.node_id = node_id

    def set_NodeId(self, node_id):
        self.node_id = node_id

    def get_NodeId(self):
        return self.node_id


