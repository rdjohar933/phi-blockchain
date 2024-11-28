#Creating blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#Todo : add a class model for² block
class Blockchain :

    def __init__(self):
        self.chain = []
        self.transactions = []
        block = self.mine_new_bock({'index':len(self.chain) + 1, 'timestamp' : str(datetime.datetime.now()), 'proof' : 1, 'previous_hash':'0', 'transactions' : self.transactions})
        self.create_block(block)
        self.nodes = set()

    #Todo : rename this method to append_block since it no longer creates the block
    def create_block(self, block):
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def mine_new_bock(self, previous_block)->dict:
        new_proof = 1
        check_proof = False
        block = None
        while not check_proof :
            previous_hash = self.hash(previous_block)
            block = {'index' : len(self.chain) + 1,
                     'timestamp' : str(datetime.datetime.now()),
                     'proof' : new_proof,
                     'previous_hash' : previous_hash,
                     'transactions' : self.transactions}
            hash_operation = self.hash(block)
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof +=1
        self.transactions = []
        return block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()


    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            hash_operation = self.hash(block)
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.chain.append({'sender': sender,
                           'receiver': receiver,
                           'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
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



# Mining our Blockchain

app = Flask(__name__)

node_address = str(uuid4()).replace('-','')

blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    #Todo : Verify that adding the transaction doesn't break the hash compatibility (if so, add the transaction during the mining attempts)
    blockchain.add_transaction(sender=node_address, receiver='Reda', amount=1)
    block_mined = blockchain.mine_new_bock(previous_block)
    block = blockchain.create_block(block_mined)
    response = {'message': 'You mined successfully !',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The blockchain is valid.'}
    else:
        response = {'message': 'We have a problem. The blockchain is not valid.'}
    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    body = request.get_json()
    transaction_keys =['sender', 'receiver', 'amount']
    if not all (key in body for key in transaction_keys ):
        return 'Some elements are missing!', 400

    index = blockchain.add_transaction(body['sender'], body['receiver'], body['amount'])
    response = {'message': f'This transaction will be added to block {index}'}

    return jsonify(response), 201

@app.route('/connect_node', methods=['POST'])
def connect_node():
    body = request.get_json()
    nodes = body.get('nodes')
    if nodes is None:
        return 'No nodes!', 400

    for node in nodes:
        blockchain.add_node(node)

    index = blockchain.add_transaction(body['sender'], body['receiver'], body['amount'])
    response = {'message': f'All nodes are now connected.',
                'nodes': list(blockchain.nodes)}

    return jsonify(response), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_replaced = blockchain.replace_chain()
    if is_replaced:
        response = {'message': 'The nodes have different chains. The chains are replaced with the longest valid chain.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The nodes have the same chains. Nothing was replaced.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

app.run(host= '0.0.0.0', port= 5001)