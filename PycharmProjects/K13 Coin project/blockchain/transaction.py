import hashlib
import uuid


class Transaction:
    """
    Transactions contain either data about money transfers or new wallet creations (Nodes).
    """

    def __init__(self, private_key=None, public_key=None, node=None, sender=None, receiver=None, amount=None,
                 date=None):
        if node != None:
            self.node = node
        else:
            self.private_key = private_key
            self.public_key = public_key
            self.node = node
            self.sender = sender
            self.receiver = receiver
            self.amount = amount
            self.date = date
            self.signature = None

    def to_string(self):
        rand = uuid.uuid4().hex
        if self.node == None:
            return self.sender + "->" + str(self.private_key) + str(self.public_key) + rand
        return str(self.node)

    def get_sender(self):
        if self.sender != None:
            return self.sender
        return ""

    def get_receiver(self):
        if self.receiver != None:
            return self.receiver
        return ""

    def get_amount(self):
        return int(self.amount)

    def is_valid_transaction(self):
        """
        Check that the transactions aren't forged or tampered with.
        :return: True or False.
        """

        # Don't allow transactions to self
        if self.sender == self.receiver:
            return False

        # Mining rewards are always valid
        if self.sender == "Mine reward":
            return True

        # Sender has to verify with their private and public key that its sending from their wallet.
        hash = hashlib.sha256(str(self.public_key + self.private_key).encode()).hexdigest()
        if hash != self.sender:
            return False

        return True
