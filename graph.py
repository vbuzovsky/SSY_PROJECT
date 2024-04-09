import networkx as nx
from components.network_node import NetworkNode

class NetworkGraph():
    def __init__(self):
        self.G = nx.Graph()

    def re_build_graph(self, set_of_nodes):
        self.G = nx.Graph()
        self.G.add_nodes_from(set_of_nodes)

    def add_node(self, node : NetworkNode):
        self.G.add_node(node)

    def add_edge(self, node1 : NetworkNode, node2 : NetworkNode):
        self.G.add_edge(node1, node2)

    def get_nodes(self):
        return self.G.nodes()
    
    def get_edges(self):
        return self.G.edges()
    
    def remove_node(self, node : NetworkNode):
        self.G.remove_node(node)