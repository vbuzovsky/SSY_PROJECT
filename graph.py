import networkx as nx
from components.network_node import NetworkNode
import PIL
icons = {
    "coordinator": "./misc/coordinator.png",
    "router": "./misc/router.png",
    "end_device": "./misc/end_device.png",
}

class NetworkGraph():
    def __init__(self):
        self.G = nx.Graph()
        self.G.add_node(1)
        self.images = {k: PIL.Image.open(fname) for k, fname in icons.items()}

    def re_build_graph(self, set_of_nodes):
        self.G.clear()
        self.G.add_nodes_from(set_of_nodes)

        # TODO: THIS WILL ALSO WORK ONLY ON SPECIFIC LOCATION OF FIELD
        #       SHOULD BE BASED ON THE LOADED CONFIG
        # BUILD EDGES BASED ON PARENT ADDR FIELD


    def add_node(self, node : NetworkNode):
        self.G.add_node(node, image=self.images["coordinator"])

    def add_edge(self, node1 : NetworkNode, node2 : NetworkNode):
        self.G.add_edge(node1, node2)

    def get_nodes(self):
        return self.G.nodes()
    
    def get_edges(self):
        return self.G.edges()
    
    def remove_node(self, node : NetworkNode):
        self.G.remove_node(node)