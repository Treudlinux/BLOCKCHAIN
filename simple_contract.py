import hashlib
import time
import json
import argparse
import pickle


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


class Contract:
    def __init__(self, creator, beneficiary, figure, status=0):
        self.creator = creator
        self.beneficiary = beneficiary
        self.figure = figure
        self.status = status  # 表示刚创建，未转账

    def transfer(self):
        self.status = 1  # 表示已经转账
        print(f"{self.creator} transferred {self.figure} to {self.beneficiary}")

    def query_status(self):
        return {
            'creator': self.creator,
            'beneficiary': self.beneficiary,
            'figure': self.figure,
            'status': self.status
        }

    @staticmethod
    def from_dict(data):
        return Contract(data['creator'], data['beneficiary'], data['figure'], data['status'])


class Blockchain:
    def __init__(self):
        # 存储区块链
        self.chain = []
        # 存储合约
        self.contracts = []
        # 根据文件加载已有的区块
        self.load_chains()
        # 根据文件加载已有的合约
        self.load_contracts()

    def create_block(self, data):
        # 判断区块链是否为空，如果为空就让previous_hash为0
        previous_block = self.chain[-1] if self.chain else None
        previous_hash = previous_block.hash if previous_block else "0"
        # 因为合约信息不是字符串，故需要检测传入的data是否为字符串
        if isinstance(data, str):
            pass
        else:
            data = json.dumps(data)  # 否则转成JSON字符串

        block = Block(len(self.chain), previous_hash, data)
        self.chain.append(block)
        # 保存到文件
        self.save_block_to_file(block)
        return block

    def save_block_to_file(self, block):
        with open('blockchain.txt', 'a') as f:
            f.write(f"{block.index},{block.timestamp},{block.hash},{block.previous_hash},{block.data}\n")

    def save_block_to_binary(self, contract):
        # 将合约类转化成字典对象存储在pkl文件
        contract_data = contract.query_status()
        with open('block_contract_chain.pkl', 'ab') as f:
            pickle.dump(contract_data, f)

    def print_chain(self):
        for block in self.chain:
            print(f"""
            Index:{block.index},
            Timestamp:{block.timestamp},
            Data:{block.data},
            Hash:{block.hash},
            Previous Hash:{block.previous_hash}
            """)

    def add_contract(self, contract):
        # 添加合约信息到区块链中
        self.create_block(contract.query_status())
        # 把合约的内容写入文件中以便于后续再次执行该py文件时读入合约数据
        self.save_block_to_binary(contract)

    def transfer_contract(self, creator, beneficiary):
        for contract in self.contracts:
            # 找出创建者和受益人
            if contract.creator == creator and contract.beneficiary == beneficiary:
                # 调用Contract类的转账方法
                contract.transfer()
                # 添加转账后的信息到区块链中
                self.create_block(contract.query_status())
                self.save_block_to_binary(contract)

    def query_contract(self, creator, beneficiary):
        for contract in self.contracts:
            # 找出创建者和受益人
            if contract.creator == creator and contract.beneficiary == beneficiary:
                # 因为合约列表中可能存在未转账和已转账的两条合约，优先选择已转账的合约记录
                if contract.status == 0:
                    temp = contract
                if contract.status == 1:
                    return print(contract.query_status())
        return print(temp.query_status())

    def load_chains(self):
        # 清空区块链列表，以防数据错误
        self.chain.clear()
        try:
            with open("blockchain.txt", 'r') as f:
                # 读取txt文件每行
                lines = f.readlines()
                for line in lines:
                    # 修改了区块分布位置，将data属性放在了每行末尾，因为data里可能有逗号，会导致分割错误
                    parts = line.strip().split(',', 4)
                    index = int(parts[0])
                    timestamp = float(parts[1])
                    hash_val = parts[2]
                    previous_hash_val = parts[3]
                    data = parts[4]
                    block = Block(index, previous_hash_val, data)
                    block.hash = hash_val
                    block.timestamp = timestamp
                    self.chain.append(block)
            # 如果区块链不存在或者为空，初始化一个新的区块作为第一个区块
            if not self.chain:
                self.create_block("0")
        # 如果文件不存在，说明是第一次执行代码，初始化新区块
        except FileNotFoundError:
            self.create_block("0")

    def load_contracts(self):
        # 清空合约列表，以防数据错误
        self.contracts.clear()
        loadcontracts = []
        try:
            with open("block_contract_chain.pkl", 'rb') as f:
                while True:
                    try:
                        # 每行每行读取字典，即创建者、受益人、金额、状态四组键值对
                        contract_data = pickle.load(f)
                        loadcontracts.append(contract_data)
                        # 直到pkl文件读完
                    except EOFError:
                        break
        # 文件不存在即说明是第一次执行代码，此时无合约，跳过即可
        except FileNotFoundError:
            pass
        # 将字典转化成合约类
        self.contracts = [Contract.from_dict(contract) for contract in loadcontracts]


def main():
    parser = argparse.ArgumentParser(description="Blockchain smart contract system")
    parser.add_argument('--create', nargs=3, metavar=('creator', 'beneficiary', 'figure'), help='Create a new contract')
    parser.add_argument('--transfer', nargs=2, metavar=('creator', 'beneficiary'), help='Transfer a contract')
    parser.add_argument('--query', nargs=2, metavar=('creator', 'beneficiary'), help='Query a contract status')
    #   parser.add_argument('--print', action='store_true', help='Print the blockchain')

    args = parser.parse_args()
    blockchain = Blockchain()

    if args.create:
        creator, beneficiary, figure = args.create
        contract = Contract(creator, beneficiary, figure)
        blockchain.add_contract(contract)
        print("Contract created")

    if args.transfer:
        creator, beneficiary = args.transfer
        blockchain.transfer_contract(creator, beneficiary)

    if args.query:
        creator, beneficiary = args.query
        blockchain.query_contract(creator, beneficiary)


if __name__ == '__main__':
    main()
