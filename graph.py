import networkx as nx

# TODO: UNFINISHED "LAYER" ABOVE nx.Graph() object, PROBABLY REDUNDANT
class NetworkGraph():
    def __init__(self):
        self.G = nx.Graph()
     
    def add_node(self, node_address : str, node_info : dict):
        self.G.add_node(node_address, **node_info)

    def add_edge(self, address1 : str, address2 : str):
        self.G.add_edge(address1, address2)

    def get_nodes(self):
        return self.G.nodes
    
    def get_edges(self):
        return self.G.edges
    
    def remove_node(self, addr : str):
        self.G.remove_node(addr)