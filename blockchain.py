import functools
import json
import pickle  # convert python data to binary data

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification


MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]  # initialize blockchain list
        self.open_transactions = []  # open_transactions is list of transaction
        self.load_data()
        self.hosting_node = hosting_node_id

    def load_data(self):
        try:
            # mode should be 'rb' if using pickle, and txt should be p
            with open('blockchain.txt', mode='r') as f:
                # file_content = pickle.loads(f.read())
                # blockchain = file_content['chain']
                # open_transactions = file_content['ot']
                file_content = f.readlines()
                # from string to python object
                blockchain = json.loads(file_content[0][:-1])  # without '\n'
                # at this time, blockchain is a list of dict  # [{..}, {..}...]
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]  # a list of transaction object
                    # block = {...} for now
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain  # a list of block object

                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions
        # IOError is file not found error
        except (IOError, IndexError):
           pass
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            # mode should be 'rb' if using pickle, and txt should be p
            with open('blockchain.txt', mode='w') as f:
                # chain_with_dict_tx is a list of block object, which consist dict transaction
                # [tx.__dict__ for tx in block_el.transactions]
                chain_with_dict_tx = [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.chain]

                saveable_chain = [block.__dict__ for block in chain_with_dict_tx]
                # save as json data
                f.write(json.dumps(saveable_chain))  # from list to string
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(saveable_tx))  # from list ot string
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
        last_block = self.chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Try different PoW numbers and return the first valid one
        verifier = Verification()
        while not verifier.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        # self.chain   =   [block object, ...]
        # block.transactions  =  [transactions object, ...]

        participant = self.hosting_node
        # amount in blockchain
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.chain]
        # amount in open transaction
        open_tx_sender = [tx.amount for tx in self.open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)  # a list, consist all send transaction(blockchain and open transaction)
        # print(tx_sender)  # [[], [], [], [], [12.0, 2.0], [9.4], [3.0, 2.1, 1.2], []]

        amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.chain]
        amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

        # return total balance
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.chain) < 1:
            return None
        return self.chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        """
        can not use this becasue dict is not ordered object
        transaction = {
                       'sender': sender,
                       'recipient': recipient,
                       'amount': amount
        }
        """
        transaction = Transaction(sender, recipient, amount)
        verifier = Verification()
        if verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    # core feature of block chain
    # this is how it stores, how to get distributed across network
    def mine_block(self):
        """
        take all open_transactions and add to a new block, add to blockchain
        """
        last_block = self.chain[-1]
        hashed_block = hash_block(last_block)

        # proof of work before adding reward transaction
        proof = self.proof_of_work()

        # miner get reward, reward will be sent to the node which did mining
        reward_transaction = Transaction(sender='MINING', recipient=self.hosting_node, amount=MINING_REWARD)

        # now we ensure that is not managed globally but locally
        # could safely do that without risking that open transaction would be affected
        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)  # just add into open transaction
        block = Block(len(self.chain), hashed_block, copied_transactions, proof)
        self.chain.append(block)  # add block into blockchain
        self.open_transactions = []
        self.save_data()
        return True  # if true, open_transactions = []
