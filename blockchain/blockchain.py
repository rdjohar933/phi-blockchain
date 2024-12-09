# Creating blockchain
import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse

from block import Block
from transaction import Transaction


class Blockchain:
    def __init__(self):
        self.transactions = []
        self.chain : list[Block] = []

        prev_block = Block(index=len(self.chain) + 1, timestamp=datetime.datetime.now().timestamp(), proof=1, previous_hash='0',
                           transactions=self.transactions)
        block = self.mine_new_bock(prev_block)
        self.append_block(block)
        self.nodes = set()

    def append_block(self, block: Block) -> Block:
        self.chain.append(block)
        return block

    def get_previous_block(self) -> Block:
        return self.chain[-1]

    def mine_new_bock(self, previous_block: Block) -> Block:
        new_proof = 1
        check_proof = False
        block = None
        while not check_proof:
            if len(self.chain)>0:
                previous_hash = previous_block.get_hash()
            else:
                previous_hash='0'
            block = Block(index=len(self.chain) + 1, timestamp=datetime.datetime.now().timestamp(), proof=new_proof,
                          previous_hash=previous_hash, transactions=self.transactions)
            hash_operation = block.get_hash()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        self.transactions = []
        return block

    def is_chain_valid(self, chain=None) -> bool:
        if not chain:
            chain = self.chain
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block.previous_hash != previous_block.get_hash():
                return False

            hash_operation = block.get_hash()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append(Transaction(sender=sender, receiver=receiver, amount=amount))

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self) -> bool:
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                current_length = response.json()['length']
                current_chain = response.json()['chain']
                if current_length > max_length and self.is_chain_valid(current_chain):
                    max_length = current_length
                    longest_chain = current_chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
