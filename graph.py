import networkx as nx

class NetworkGraph():
    def __init__(self):
        self.G = nx.Graph()
        # G.add_nodes_from([2, 3]) --> add nodes from list, dict or set
