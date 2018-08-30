import functools
from collections import OrderedDict

from hash_util import hash_string_256, hash_block

# blockchain is list
# block is dict
# open_transactions is list of transaction
# transaction is dict
MINING_REWARD = 10

genesis_block = {'previous_hash': '',
                 'index': 0,
                 'transactions': [],
                 'proof': 100}

blockchain = [genesis_block]
open_transactions = []  # not been included in a new block yet
owner = 'wilson'
participants = {'wilson'}


def valid_proof(transactions, last_hash, proof):
    """
    to guess the hash which match requirement
    :param transactions:
    :param last_hash:
    :param proof:
    :return: true or false
    """
    # increment proof until much the requirement
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    # blockchain   =   [{...}, ...]
    # block   =   {'previous_hash': '', 'index': 0, 'transaction': []}

    # block['transactions']   =   [...] or [{'sender': sender, 'recipient': recipient, 'amount': amount}, ...]
    # tx   =   {'sender': sender, 'recipient': recipient, 'amount': amount}
    # amount in blockchain
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    # amount in open transaction
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)  # a list, consist all send transaction(blockchain and open transaction)
    # print(tx_sender)  # [[], [], [], [], [12.0, 2.0], [9.4], [3.0, 2.1, 1.2], []]

    amount_sent = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    amount_received = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

    # return total balance
    return amount_received - amount_sent


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    """
    can not use this becasue dict is not ordered object
    transaction = {
                   'sender': sender,
                   'recipient': recipient,
                   'amount': amount
    }
    """
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)]
    )
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False


# core feature of block chain
# this is how it stores, how to get distributed across network
def mine_block():
    """
    take all open_transactions and add to a new block, add to blockchain
    """
    last_block = blockchain[-1]  # {'previous_hash': '', 'index': 0, 'transaction': []}
    hashed_block = hash_block(last_block)

    # proof of work before adding reward transaction
    proof = proof_of_work()

    # miner get reward
    """
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    """
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)]
    )

    # now we ensure that is not managed globally but locally
    # could safely do that without risking that open transaction would be affected
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)  # just add into open transaction

    # we use sort_keys=True, so do not need to use OrderedDict
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,  # add open transaction into block
        'proof': proof
    }
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
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        # not including reward transaction so block['transactions'][:-1]
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
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
    print("h: Manipulate the chain")
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
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print('There are invalid transactions')
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {'previous_hash': '', 'index': 0, 'transaction': [{'sender': 'chris', 'recipient': 'Max', 'amount': 100}]}
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
