import json

from flask import Flask, jsonify, request
from uuid import uuid4

from block import Block
from blockchain import Blockchain
from transaction import Transaction
from flask_cors import CORS

# Mining our Blockchain

app = Flask(__name__)
CORS(app)
node_address = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/block', methods=['POST'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    blockchain.add_transaction(sender=node_address, receiver='phi-partners', amount=1.0)
    block_mined = blockchain.mine_new_bock(previous_block)
    block = blockchain.append_block(block_mined)
    response = {'message': 'You mined successfully !',
                'block': block
                }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {'chain': json.loads(Block.schema().dumps(blockchain.chain, many=True)),
                'length': len(blockchain.chain)}
    return jsonify(response), 200


@app.route('/validity', methods=['GET'])
def is_valid():
    status = blockchain.is_chain_valid()
    if status:
        response = {'message': 'All good. The blockchain is valid.'}
    else:
        response = {'message': 'We have a problem. The blockchain is not valid.'}
    return jsonify(response), 200


@app.route('/hash', methods=['POST'])
def hash_block():
    body = request.get_data(as_text=True)
    try:
        block = Block.from_json(body)
        hash = block.get_hash()
        return jsonify({"block": block, "hash":hash}), 200
    except ValueError:
        return jsonify({'error': 'Bad request', "block": body}), 400


@app.route('/transaction', methods=['POST'])
def add_transaction():
    body = request.get_data(as_text=True)
    try:
        transaction = Transaction.from_json(body)
        blockchain.add_transaction(transaction.sender, transaction.receiver, transaction.amount)
        response = {'message': f'This transaction will be added to block {len(blockchain.chain)+1}'}
        return jsonify(response), 201
    except ValueError:
        return jsonify({'error': 'Bad request'}), 400


@app.route('/connect', methods=['POST'])
def connect_node():
    body = request.get_json()
    nodes = body.get('nodes')
    if nodes is None:
        return 'No nodes!', 400

    for node in nodes:
        blockchain.add_node(node)

    response = {'message': f'All nodes are now connected.',
                'nodes': list(blockchain.nodes)}

    return jsonify(response), 201


@app.route('/chain', methods=['POST'])
def replace_chain():
    is_replaced = blockchain.replace_chain()
    if is_replaced:
        response = {'message': 'The nodes have different chains. The chains are replaced with the longest valid chain.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The nodes have the same chains. Nothing was replaced.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


def main(port):
    print(f"I am node {node_address}")
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main(port=5001)
