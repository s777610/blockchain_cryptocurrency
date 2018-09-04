
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii  # convert binary data into string


class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet.txt', mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
            except (IOError, IndexError):
                print('Saving wallet failed...')

    def load_keys(self):
        try:
            with open('wallet.txt', mode='r') as f:
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
        except (IOError, IndexError):
            print('Loading wallet failed...')

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
                binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))
    """
    pass private_key to signer
    pass public_key to verifier
    """
    def sign_transaction(self, sender, recipient, amount):
        # binascii.unhexlify can convert sting to binary
        # signer to sign transaction
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        # encode can encode it to binary string
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(h)
        # decode into string
        return binascii.hexlify(signature).decode('ascii')  # this is signature string

    @staticmethod  # we don't access class here
    def verify_transaction(transaction):
        # we don't verify this because this transaction does not have signature
        if transaction.sender == 'MINING':
            return True
        # use binascii.unhexlify to convert string to binary
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))  # transaction.sender is public_key
        # verifier to verify transaction
        verifier = PKCS1_v1_5.new(public_key)  # public_key is binary here
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
        # use binascii.unhexlify to convert it from string to binary
        # the signature here is what we want to verify
        return verifier.verify(h, binascii.unhexlify(transaction.signature))
