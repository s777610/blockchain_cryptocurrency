import functools
import json
import pickle  # convert python data to binary data

from hash_util import hash_string_256, hash_block
from block import Block
from transaction import Transaction


# blockchain is list
# open_transactions is list of transaction
# transaction is dict
MINING_REWARD = 10

blockchain = []
open_transactions = []  # not been included in a new block yet
owner = 'wilson'
participants = {'wilson'}


def load_data():
    global blockchain
    global open_transactions
    try:
        # mode should be 'rb' if using pickle, and txt should be p
        with open('blockchain.txt', mode='r') as f:
            # file_content = pickle.loads(f.read())
            # blockchain = file_content['chain']
            # open_transactions = file_content['ot']
            file_content = f.readlines()
            # from string to python object
            # blockchain is a list of dict [{}, {},...]
            blockchain = json.loads(file_content[0][:-1])  # without '\n'
            # at this time, blockchain is a list of dict  # [{..}, {..}...]
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]  # a list of transaction object
                # block = {...}
                updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain  # a list of block object

            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                updated_transactions.append(updated_transaction)
            open_transactions = updated_transactions
    # IOError is file not found error
    # IndexError handle in case of empty file
    except (IOError, IndexError):
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]
        open_transactions = []  # not been included in a new block yet

load_data()


def save_data():
    try:
        # mode should be 'rb' if using pickle, and txt should be p
        with open('blockchain.txt', mode='w') as f:

            # chain_with_dict_tx is a list of block object, which consist dict transaction
            chain_with_dict_tx = [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in blockchain]

            saveable_chain = [block.__dict__ for block in chain_with_dict_tx]
            # save as json data
            f.write(json.dumps(saveable_chain))  # from list to string
            f.write('\n')
            saveable_tx = [tx.__dict__ for tx in open_transactions]
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


def valid_proof(transactions, last_hash, proof):
    """
    to guess the hash which match requirement
    """
    # increment proof until much the requirement
    guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0:2] == '00'


def proof_of_work():
    """
    Generate a proof of work for the open transactions,
    the hash of the previous block and a random number (which is guessed until it fits).
    """
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    # Try different PoW numbers and return the first valid one
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    # blockchain   =   [block object, ...]
    # block.transactions  =  [transactions object, ...]

    # amount in blockchain
    tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in blockchain]
    # amount in open transaction
    open_tx_sender = [tx.amount for tx in open_transactions if tx.sender == participant]
    tx_sender.append(open_tx_sender)  # a list, consist all send transaction(blockchain and open transaction)
    # print(tx_sender)  # [[], [], [], [], [12.0, 2.0], [9.4], [3.0, 2.1, 1.2], []]

    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in blockchain]
    amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

    # return total balance
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction.sender)
    return sender_balance >= transaction.amount


def add_transaction(recipient, sender=owner, amount=1.0):
    """
    can not use this becasue dict is not ordered object
    transaction = {
                   'sender': sender,
                   'recipient': recipient,
                   'amount': amount
    }
    """
    transaction = Transaction(sender, recipient, amount)
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


# core feature of block chain
# this is how it stores, how to get distributed across network
def mine_block():
    """
    take all open_transactions and add to a new block, add to blockchain
    """
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)

    # proof of work before adding reward transaction
    proof = proof_of_work()

    # miner get reward
    reward_transaction = Transaction(sender='MINING', recipient=owner, amount=MINING_REWARD)

    # now we ensure that is not managed globally but locally
    # could safely do that without risking that open transaction would be affected
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)  # just add into open transaction
    block = Block(len(blockchain), hashed_block, copied_transactions, proof)
    blockchain.append(block)  # add block into blockchain
    return True  # if true, open_transactions = []


def get_transaction_value():
    tx_recipient = input('Enter the recipient of the transaction: ')
    tx_amount = float(input("Your transaction amount please: "))
    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    # output the blockchain list to the console
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    """ verify entire blockchain"""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        # not including reward transaction so block['transactions'][:-1]
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            print("Proof of work is invalid")
            return False

    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True

while waiting_for_input:
    print("Please choose")
    print("1: Add a new transaction value")
    print("2: Mine a new block")
    print("3: Output the blockchain blocks")
    print("4: Output participants")
    print("5: Check transaction validity")
    print("q: Quit")
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There are invalid transactions')
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print("Invalid Blockchain!")
        break
    # :6 = 6 digits for it, .2f = only show two decimal places
    print('Balance of {}: {:6.2f}'.format('wilson', get_balance('wilson')))
else:
    print('User left!')

print('Done!')
