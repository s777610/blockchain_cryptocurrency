import functools
import json

from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet


MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):  # hosting_node is public_key
        genesis_block = Block(0, '', [], 100, 0)
        # __open_transactions should only be accessed within this class
        self.chain = [genesis_block]  # initialize blockchain list
        self.__open_transactions = []  # open_transactions is list of transaction, not including reward
        self.load_data()
        self.hosting_node = hosting_node_id

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
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]  # a list of transaction object
                    # block = {...} for now
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain  # a list of block object will be loaded by setter

                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
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
                chain_with_dict_tx = [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]

                saveable_chain = [block.__dict__ for block in chain_with_dict_tx]
                # save as json data
                f.write(json.dumps(saveable_chain))  # from list to string
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
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
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # Try different PoW numbers and return the first valid one
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        participant = self.hosting_node

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

    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """
        can not use this becasue dict is not ordered object
        transaction = {
                       'sender': sender,
                       'recipient': recipient,
                       'amount': amount
        }
        """
        if self.hosting_node == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    # core feature of block chain
    # this is how it stores, how to get distributed across network
    def mine_block(self):
        """
        take all open_transactions and add to a new block, add to blockchain
        """
        if self.hosting_node == None:
            return False
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)

        # proof of work before adding reward transaction
        proof = self.proof_of_work()

        # miner get reward, reward will be sent to the node which did mining
        # we never verify signature here
        reward_transaction = Transaction(sender='MINING', recipient=self.hosting_node, signature='', amount=MINING_REWARD)

        # now we ensure that is not managed globally but locally
        # could safely do that without risking that open transaction would be affected
        copied_transactions = self.__open_transactions[:]

        # loop check all transactions(not include reward transactions) which will be added in next block
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                return False
        copied_transactions.append(reward_transaction)  # just add into open transaction

        block = Block(index=len(self.__chain), previous_hash=hashed_block, transactions=copied_transactions, proof=proof)

        self.__chain.append(block)  # add new block into blockchain
        self.__open_transactions = []
        self.save_data()
        return True
