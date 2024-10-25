import hashlib
from datetime import datetime
import pickle
import json

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
        self.create_block(data={}, previous_hash='0')

    def create_block(self, data, previous_hash):
        index = len(self.chain) + 1
        timestamp = datetime.now().isoformat()
        hash_string = f'{index}{previous_hash}{timestamp}{str(data)}'.encode()  
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

    def update_data(self, athlete_data):
        athlete_id = athlete_data.get('id')
        for block in self.chain[1:]:  # Skip the genesis block
            existing_data = json.loads(block.data)
            if existing_data.get('id') == athlete_id:
                block.data = json.dumps(athlete_data)  # Update the existing block
                return
        # If athlete not found, add a new block
        self.add_data(json.dumps(athlete_data))

    def get_leaderboard(self):
        leaderboard = []
        for block in self.chain[1:]:  # Skip the genesis block
            athlete_data = json.loads(block.data)
            leaderboard.append(athlete_data)
        return leaderboard

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