import hashlib
import math

def is_power_of_two(n):
    return (n & (n-1) == 0) and n != 0

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def create_node(data, get_next_counter, hash_function_leaves, hash_function_nodes):
    return LeafNode(hash_function_leaves, data[0], "L", get_next_counter) \
        if len(data) == 1 \
        else IntermediaryNode(data, "H", get_next_counter, hash_function_leaves, hash_function_nodes)
class LeafNode:
    """Simple class that represents a Merkle Tree leaf node"""
    def __init__(self, hash_function_leaves, data, name, get_next_counter):
        self.value = hash_function_leaves(str(data).encode('utf-8')).hexdigest()
        self.name = name + "<sub>" + str(get_next_counter()) + "</sub>"
        self.data = data
        self.left = None
        self.right = None
        self.display = "H(" + self.data + ")"
        self.layers = 1

    def __str__(self):
        return self.name + " = " + self.value


class IntermediaryNode:
    """Simple class that represents a Merkle Tree node"""
    def __init__(self, data, name, get_next_counter, hash_function_leaves=hashlib.sha256, hash_function_nodes=None):
        if (not is_power_of_two(len(data))):
            raise Exception("Not power of 2 not supported")
        self.data = data
        self.left = create_node(data[0:len(data)//2], get_next_counter, hash_function_leaves, hash_function_nodes) 
        self.name = name + "<sub>" + str(get_next_counter()) + "</sub>"
        self.right = create_node(data[len(data)//2:], get_next_counter, hash_function_leaves, hash_function_nodes) 
        self.hash_function_nodes = hash_function_nodes or hash_function_leaves
        self.hash_function_leaves = hash_function_leaves
        self.value = self.__hash_pair(self.left.value, self.right.value)
        self.display = "H(" + self.left.name + "|" + self.right.name + ")"

        self.layers = self.left.layers + 1

    def get_proof(self, data_index):
        bits = [int(d) for d in str(bin(data_index))[2:].zfill(self.layers)]
        return self.__get_proof(bits)

    def __get_proof(self, path):
        value = node.left.value if b == 1 else node.right.value
        node = node.left if b == 0 else node.right

        return [value] + node.__get_proof(path[1:]) 

    def verify(self, key, proof):
        current_hash_value = self.hash_function_leaves(str(key).encode('utf-8')).hexdigest()
        
        for p in proof:
            current_hash_value = self.__hash_pair(current_hash_value, p)
        
        return current_hash_value == self.root.value
    
    def __hash_pair(self, node1: str, node2: str):
        return self.hash_function_nodes(str(node1).encode('utf-8') + str(node2).encode('utf-8')).hexdigest() \
            if node1 <= node2 \
            else self.hash_function_nodes(str(node2).encode('utf-8') + str(node1).encode('utf-8')).hexdigest()

    
    def __str__(self):
        return self.name + " = " + self.value

name_counter = 0
class MerkleTree:
    """Class that represents a merkle tree that preserves the data"""
    def __init__(self, data, hash_function_leaves=hashlib.sha256, hash_function_nodes=None):
        global name_counter
        name_counter = 0
        def get_next_counter():
            global name_counter
            name_counter += 1
            return name_counter
        self.root = IntermediaryNode(data, "R", get_next_counter, hash_function_leaves, hash_function_nodes)