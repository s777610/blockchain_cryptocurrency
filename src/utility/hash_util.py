import hashlib
import json


def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()


# proof_of_work will call this func
def hash_block(block):
    # return '-'.join([str(block[key]) for key in block])
    # use json.dumps to convert dict obj to json(string)
    """
    copy() is used to get a new dictionary - otherwise,
    changes will affect the old dictionary and can lead to unwanted side effects
    (i.e. changes in this place having impact on the data in your running application/blockchain).
    You should be able to observe this if you omit copy().

    if not use copy(), when ever you hash a block,
    this hashable_block will overwrite the
    previous reference to previous dictionary
    it got for last block it hashed
    so for next block you are hashing
    you also change something about last block
    """
    hashable_block = block.__dict__.copy()  # {'index': 2, 'previous_hash': ...., 'transactions':[tx object, ...]}

    # now converting tx object to ordered_dict, that is why make a copy without changing hashable_block
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())

