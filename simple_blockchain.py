import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, data):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block("0")

    def create_block(self, data):
        previous_block = self.chain[-1] if self.chain else None
        previous_hash = previous_block.hash if previous_block else "0"
        block = Block(len(self.chain), previous_hash, data)
        self.chain.append(block)
        self.save_block_to_file(block)
        return block

    def save_block_to_file(self,block):
        with open('simple_blockchain.txt', 'a') as f:
            f.write(f"{block.index},{block.timestamp},{block.data},{block.hash},{block.previous_hash}\n")

    def print_chain(self):
        for block in self.chain:
            print(f"""
            Index:{block.index},
            Timestamp:{block.timestamp},
            Data:{block.data},
            Hash:{block.hash},
            Previous Hash:{block.previous_hash}
            """)

#创建区块链并添加区块
blockchain = Blockchain()
blockchain.create_block("First block data")
blockchain.create_block("Second block data")
blockchain.print_chain()
