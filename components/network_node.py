
class NetworkNode:
    def __init__(self, header, data):
        self.header = header
        self.data = data

    # TODO: THIS IS BUGGY, EXPECTS FULL ADDRESS ON THE INDEX 2 IN THE HEADER
    def __hash__(self) -> int:
        continuous_string = ''.join([x[2:] for x in self.header[2][-1]])
        print("Trying to hash following sequence: ", continuous_string)
        h = hash(continuous_string)
        print("Creating new node with hash: ", h)
        return h
    
    def __eq__(self, other) -> bool:
        return self.__hash__() == other.__hash__()
    
    def __repr__(self) -> str:
        return "Node with full address: " + str(self.header[2][-1])