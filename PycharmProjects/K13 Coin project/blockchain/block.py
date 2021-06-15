import hashlib

class Block:
    """
    A Block is a block of a Transition object and a previous hash from the previous block.
    Blocks contain their block height, hashed transaction data and the previous block's hash.
    """

    def __init__(self, transaction, previous_hash):
        self.transaction = transaction
        self.hash = hashlib.sha256(transaction.to_string().encode()).hexdigest()
        self.previous_hash = previous_hash
        self.block_number = None

    def get_hash(self):
        return self.hash

    def get_previous_hash(self):
        return self.previous_hash

    def get_transaction_data(self):
        return self.transaction

    def get_block_number(self):
        return self.block_number

    def set_block_number(self, number):
        self.block_number = number

    def set_hash(self, hash):
        self.hash = hash
