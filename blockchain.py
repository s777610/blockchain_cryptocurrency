# blockchain is list
# block is dict
# open_transactions is list of transaction
# transaction is dict

genesis_block = {'previous_hash': '',
                 'index': 0,
                 'transaction': []}
blockchain = [genesis_block]
open_transactions = []  # not been included in a new block yet
owner = 'wilson'
participants = {'wilson'}


def hash_block(block):
    return '-'.join([str(block[key]) for key in block])


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    transaction = {
                   'sender': sender,
                   'recipient': recipient,
                   'amount': amount
    }
    open_transactions.append(transaction)
    participants.add(sender)
    participants.add(recipient)


# core feature of block chain
# this is how it stores, how to get distributed across network
def mine_block():
    """
    take all open_transactions and add to a new block, add to blockchain
    """
    last_block = blockchain[-1]  # {'previous_hash': '', 'index': 0, 'transaction': []}
    hashed_block = hash_block(last_block)
    block = {
             'previous_hash': hashed_block,
             'index': len(blockchain),
             'transaction': open_transactions
    }
    blockchain.append(block)


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
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
    return True




waiting_for_input = True

while waiting_for_input:
    print("Please choose")
    print("1: Add a new transaction value")
    print("2: Mine a new block")
    print("3: Output the blockchain blocks")
    print("4: Output participants")
    print("h: Manipulate the chain")
    print("q: Quit")
    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        add_transaction(recipient, amount=amount)
        print(open_transactions)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
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
else:
    print('User left!')

print('Done!')
