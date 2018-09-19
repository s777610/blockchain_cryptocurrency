import functools
import json
import requests

from utility.hash_util import hash_block
from models.block import Block
from models.transaction import Transaction
from utility.verification import Verification
from models.wallet import Wallet


MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):  # hosting_node is public_key
        genesis_block = Block(0, '', [], 100, 0)
        # __open_transactions should only be accessed within this class
        self.chain = [genesis_block]  # initialize blockchain list
        self.__open_transactions = []  # open_transactions is list of transaction, not including reward
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    """
    if you want to control access for both reading and writing, you can use @property
    python create private property, and gives us getter and setter
    Notice: __chain is created automatically by this
    """
    # this is getter
    # when I try to get value for chain, this code is executed
    @property
    def chain(self):
        return self.__chain[:]

    # this is setter
    # when I try to set something to chain, this code is executed
    # therefore, we can load data and overwrite entire chain
    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            # mode should be 'rb' if using pickle, and txt should be p
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
                # file_content = pickle.loads(f.read())
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
                file_content = f.readlines()
                # from string to python object
                blockchain = json.loads(file_content[0][:-1])  # without '\n'
                # at this time, blockchain is a list of dict  # [{..}, {..}...]
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]  # a list of transaction object
                    # block = {...} for now
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain  # a list of block object will be loaded by setter

                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions

                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)

        # IOError is file not found error
        except (IOError, IndexError):
           pass
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            # mode should be 'rb' if using pickle, and txt should be p
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                # chain_with_dict_tx is a list of block object, which consist dict transaction
                # [tx.__dict__ for tx in block_el.transactions]
                chain_with_dict_tx = [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]

                saveable_chain = [block.__dict__ for block in chain_with_dict_tx]
                # save as json data
                f.write(json.dumps(saveable_chain))  # from list to string
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))  # from list ot string
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
                """
                save as binary data
                save_data = {
                    'chain': blockchain,
                    'ot': open_transactions
                }
                f.write(pickle.dumps(save_data))
                """
        except IOError:
            print('Saving failed!')

    def proof_of_work(self):
        """
        Generate a proof of work for the open transactions,
        the hash of the previous block and a random number (which is guessed until it fits).
        """
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Try different PoW numbers and return the first valid one
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self, sender=None):
        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender
        # self.__chain   =   [block object, ...]
        # block.transactions  =  [transactions object, ...]
        # amount in blockchain
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        # amount in open transaction
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)  # a list, consist all send transaction(blockchain and open transaction)
        # print(tx_sender)  # [[], [], [], [], [12.0, 2.0], [9.4], [3.0, 2.1, 1.2], []]
        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

        # return total balance
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """
        can not use this becasue dict is not ordered object
        transaction = {
                       'sender': sender,
                       'recipient': recipient,
                       'amount': amount
        }
        """
        # if self.public_key == None:
        #     return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()

            # only broadcast to peer node if we are on the node where we originally create that transaction
            if not is_receiving:
                # broadcast transaction to each peer node
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={'sender': sender, 'recipient': recipient,
                                                 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Broadcast transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:  # the server of node is not running
                        continue  # this node does not running, others may do, so continue
            return True
        return False

    # core feature of block chain
    # this is how it stores, how to get distributed across network
    def mine_block(self):
        """
        take all open_transactions and add to a new block, add to blockchain
        """
        if self.public_key is None:
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        # proof of work before adding reward transaction
        proof = self.proof_of_work()

        # miner get reward, reward will be sent to the node which did mining
        # we never verify signature here
        reward_transaction = Transaction(sender='MINING', recipient=self.public_key, signature='', amount=MINING_REWARD)

        # now we ensure that is not managed globally but locally
        # could safely do that without risking that open transaction would be affected
        copied_transactions = self.__open_transactions[:]

        # loop check all transactions(not include reward transactions) which will be added in next block
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)  # just add into open transaction

        block = Block(index=len(self.__chain), previous_hash=hashed_block,
                      transactions=copied_transactions, proof=proof)

        self.__chain.append(block)  # add new block into blockchain
        self.__open_transactions = []
        self.save_data()
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Broadcast block declined, needs resolving')
                if response.status_code == 409:  # 409 means conflict
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):  # block is dict here
        # transactions is a list of transaction object
        transactions = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)

        """
        update open transaction on peer node, when broadcast block to peer node
        the some open transactions on peer node should be removed because it will be store in new block
        """
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:  # itx is incoming tx
            for opentx in stored_transactions:  # opentx is open transaction of node
                # for every incoming transaction, check if it is part of my open transaction
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    # if same, try removing it from peer node to prevent encountering second time
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True

    def resolve(self):
        winner_chain = self.chain
        replace = False  # whether our current chain is getting replaced, initially is False
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()  # list of block dict
                # create list of block object with a list of dict transaction
                node_chain = [Block(block['index'],
                                    block['previous_hash'],
                                    [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']],
                                    block['proof'],
                                    block['timestamp']) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True  # if replace is True, we can assume our transactions are incorrect

            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []  # if chain is replaced, set local open tx to []
        self.save_data()
        return replace

    def add_peer_node(self, node):
        """Adds a new node to the peer node set.
        Arguments:
            node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """return a list of all connected peer nodes."""
        return list(self.__peer_nodes)[:]
