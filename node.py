
from flask import Flask, jsonify
from wallet import Wallet

# only clients running on same server can access this server
# only web pages html returned by a server can again send requests to it
from flask_cors import CORS  # Cross-Origin Resource Sharing
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


# pass path and type of request
@app.route('/', methods=['GET'])
def get_ui():
    return 'This works!'


@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_block()  # mine block return block
    if block != None:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': dict_block
        }
        return jsonify(response), 201  # 201 successfully create something
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    # convert block into dict, however transaction still is object
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]  # list of block dict
    for dict_block in dict_chain:
        # convert list of tx object to list of tx dict
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]

    return jsonify(dict_chain), 200





if __name__ == '__main__':
    # run() take 2 args, IP and port
    app.run(host='0.0.0.0', port=5000)


