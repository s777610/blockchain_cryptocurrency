from uuid import uuid4
from blockchain import Blockchain
from verification import Verification


class Node:
    """
    every node is a computer having its local blockchain instance,
    where you can mine block and send transactions
    therefore, it make sense  that we have a node class
    """

    def __init__(self):
        # self.id = str(uuid4())
        self.id = 'wilson'
        self.blockchain = Blockchain(self.id)

    def get_transaction_value(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input("Your transaction amount please: "))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    def print_blockchain_elements(self):
        # output the blockchain list to the console
        for block in self.blockchain.chain:  # this execute getter
            print('Outputting Block')
            print(block)
        else:
            print('-' * 20)

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print("Please choose")
            print("1: Add a new transaction value")
            print("2: Mine a new block")
            print("3: Output the blockchain blocks")
            print("4: Check transaction validity")
            print("q: Quit")
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()  # from user input
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient=recipient, sender=self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(open_transactions=self.blockchain.get_open_transactions(),
                                                    get_balance=self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions')
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            if not Verification.verify_chain(blockchain=self.blockchain.chain):
                self.print_blockchain_elements()
                print("Invalid Blockchain!")
                break
            # :6 = 6 digits for it, .2f = only show two decimal places
            print('Balance of {}: {:6.2f}'.format(self.id, self.blockchain.get_balance()))
        else:
            print('User left!')

        print('Done!')


node = Node()
node.listen_for_input()