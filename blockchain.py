import hashlib
from datetime import datetime
import pickle

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(data="Genesis Block", previous_hash='0')

    def create_block(self, data, previous_hash):
        index = len(self.chain) + 1
        timestamp = datetime.now().isoformat()
        hash_string = f'{index}{previous_hash}{timestamp}{data}'.encode()  
        hash_value = hashlib.sha256(hash_string).hexdigest()
        new_block = Block(index, previous_hash, timestamp, data, hash_value)
        self.chain.append(new_block)
        return new_block

    def get_last_block(self):
        return self.chain[-1]

    def add_data(self, data):
        last_block = self.get_last_block()
        previous_hash = last_block.hash
        self.create_block(data, previous_hash)

    def print_chain(self):
        for block in self.chain:
            print(f"Block #{block.index}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash: {block.hash}")
            print("\n")

    def save_blockchain(self, filename='blockchain.pkl'):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load_blockchain(filename='blockchain.pkl'):
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return Blockchain()