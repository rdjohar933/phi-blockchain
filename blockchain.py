#Creating blockchain
import datetime
import hashlib
import json
from operator import index

from flask import Flask, jsonify

class Blockchain :

    def __init__(self):
        self.chain = []
        self.create_block({'index':len(self.chain) + 1, 'timestamp' : str(datetime.datetime.now()), 'proof' : 1, 'previous_hash':'0',})

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
            previous_hash = self.hash(json.dumps(previous_block))
            block = {'index' : len(self.chain) + 1,
                     'timestamp' : str(datetime.datetime.now()),
                     'proof' : new_proof,
                     'previous_hash' : previous_hash}
            hash_operation = self.hash(json.dumps(block))
            #hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof +=1
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

            #Todo : adapt this check to handle the whole block instead of the nonce
            previous_proof = previous_block['proof']
            current_proof = block['proof']
            hash_operation = hashlib.sha256(str(current_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

# Mining our Blockchain

app = Flask(__name__)

blockchain = Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    #previous_proof = previous_block['proof']
    block_mined = blockchain.mine_new_bock(previous_block)
    #previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(block_mined)
    response = {'message': 'You mined successfully !',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash':block['previous_hash']}
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

app.run()