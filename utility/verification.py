
from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet


# just a helper class, no need to create object
# having it just for grouping funcs
class Verification:

    @staticmethod  # not accessing anything from the class
    def valid_proof(transactions, last_hash, proof):
        """
        to guess the hash which match requirement
        """
        # increment proof until much the requirement
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        return guess_hash[0:2] == '00'

    @classmethod  # not need a instance here
    def verify_chain(cls, blockchain):
        """ verify entire blockchain"""
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            # not including reward transaction so block['transactions'][:-1]
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print("Proof of work is invalid")
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        if check_funds:
            sender_balance = get_balance()  # amount_received - amount_sent
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        # check_funds is False because we don't need to check funds here, just check signature
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])

