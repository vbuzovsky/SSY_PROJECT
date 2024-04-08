
class NetworkNode:
    def __init__(self, header, data):
        self.header = header
        self.data = data
    
    def __hash__(self) -> int:
        return hash(self.header[1:])
    
    def __eq__(self, other) -> bool:
        return self.header == other.header and self.data == other.data