import datetime
import time
from urllib.parse import urlparse
from block import *
from transaction import *
from mnemonic import Mnemonic

class Blockchain:
    """
    The blockchain has methods that handle every transaction and node creation in the network.
    """
    #Set the mining difficulty.
    DIFFICULTY = 4

    # __init__ function has Fields which can be accessed by self.field
    def __init__(self):
        self.blockchain_list = []
        self.unconfirmed_blockchain = []
        self.unconfirmed_transactions = []
        self.confirmed_transactions = []
        self.nodes = set()

    def add_unconfirmed_block(self, block):
        self.unconfirmed_blockchain.append(block)

    def add_block(self, block):
        self.blockchain_list.append(block)

    def register_node(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    def get_unconfirmed_transactions(self, wallet_address):
        self.unconfirmed_transactions.clear()
        for block in self.unconfirmed_blockchain:
            transaction = {}
            if block.get_transaction_data().get_receiver() == wallet_address:
                transaction[block.get_hash()] = int(block.get_transaction_data().get_amount())
                self.unconfirmed_transactions.append(transaction)

            elif block.get_transaction_data().get_sender() == wallet_address:
                transaction[block.get_hash()] = (-1) * int(block.get_transaction_data().get_amount())
                self.unconfirmed_transactions.append(transaction)

        return self.unconfirmed_transactions

    def get_confirmed_transactions(self, wallet_address):
        self.confirmed_transactions.clear()
        for block in self.blockchain_list:
            transaction = {}
            if block.get_hash().startswith("0000"):
                if block.get_transaction_data().get_receiver() == wallet_address:
                    transaction[block.get_hash()] = int(block.get_transaction_data().get_amount())
                    self.confirmed_transactions.append(transaction)

                elif block.get_transaction_data().get_sender() == wallet_address:
                    transaction[block.get_hash()] = (-1) * int(block.get_transaction_data().get_amount())
                    self.confirmed_transactions.append(transaction)

        return self.confirmed_transactions

    def create_node(self):
        """
        Create a new node with a public key, private key and mnemonics.
        Gives the user a one time dictionary with private information about their wallet.
        This information is temporary as it prompts the user to save the information in case they want to reopen the wallet.
        :return: A dictionary that contains private information about the wallet that was generated.
        """
        mnemonic = Mnemonic("english")
        words = mnemonic.generate(strength=256)
        seed = mnemonic.to_seed(words, passphrase="")
        entropy = mnemonic.to_entropy(words)
        public_key = self.generate_hash_byte(seed)
        private_key = self.generate_hash_byte(entropy)
        key_identifier = public_key + private_key

        transaction = Transaction(None, None, key_identifier)
        block = Block(transaction, self.get_previous_hash())
        self.add_block(block)
        block_height = self.get_current_block_height()

        self.make_transaction(0, 0, "Mine reward", block.get_hash(), 100)

        identifiers = {"public_key": public_key, "private_key": private_key, "words": words, "block_height": block_height, "wallet_address": block.get_hash()}
        return identifiers



    def get_wallet_balance(self, wallet):
        """
        Gets balance of a given wallet by going through the blockchain and comparing
        every transaction that has been made from that wallet.
        :param wallet: Wallet address to check balance.
        :return: The wallet's current address.
        """
        balance = 0
        #Go through the blockchain and find all of the wallet's transactions.
        for block in self.blockchain_list:
            if block.get_hash().startswith("0000"):
                #If the wallet has recieved coins, add them to the balance.
                if block.get_transaction_data().get_receiver() == wallet:
                    balance += block.get_transaction_data().get_amount()

                #If the wallet has sent coins, reduce it from the balance.
                elif block.get_transaction_data().get_sender() == wallet:
                    balance -= block.get_transaction_data().get_amount()

        return balance

    def can_send(self, wallet, coins):
        """
        Check if the wallet has enough balance to send
        :param wallet: Address of the wallet to check.
        :return:
        """
        balance = self.get_wallet_balance(wallet)
        if balance >= int(coins):
            return True
        return False

    def make_transaction(self, private_key, public_key, sender, receiver, amount):
        try:
            int(amount)
        except:
            print("NOT LEGIT INTEGER")
            return "x"
        if sender == "Mine reward" or self.can_send(sender, amount):
            self.add_transaction(private_key, public_key, sender, receiver, amount)
        else:
            print("NO BALANCE!!!!!!!!!!")

    def add_transaction(self, private_key, public_key, sender, receiver, amount):
        transaction = Transaction(private_key, public_key, None, sender, receiver, amount, str(datetime.date.today()))
        if (transaction.is_valid_transaction() and self.is_in_blockchain(sender) and self.is_in_blockchain(receiver)) or sender == "Mine reward":
            block = Block(transaction, self.get_previous_unconfirmed_hash())
            self.add_unconfirmed_block(block)
            print("Added transaction: " + str(block))

        else:
            print("Transaction is illegal")

    def is_in_blockchain(self, wallet_address):
        for block in self.blockchain_list:
            if block.get_hash() == wallet_address:
                return True
        return False

    def generate_hash_byte(self, byte_to_hash):
        hash = hashlib.sha256(byte_to_hash).hexdigest()
        return hash

    def generate_hash(self, item_to_hash):
        hash = hashlib.sha256(item_to_hash.encode()).hexdigest()
        return hash

    def mine_oldest_block(self, wallet_address):
        if self.unconfirmed_blockchain == []:
            print("No blocks to be confirmed")
        else:
            self.mine(self.get_unconfirmed_block_by_height(0), self.DIFFICULTY, wallet_address)

    def mine(self, block, prefix_zeros, wallet_address):
        """
        Mine a block in the blockchain by using proof of work.
        :param wallet_address:
        :param blockchain: The blockchain.
        :param block: Block to mine.
        :param prefix_zeros: the difficulty of the block.
        :return: If block was mined or not.
        """
        MAX_NONCE = 1000000000
        zeros = "0" * prefix_zeros
        transaction = block.get_transaction_data()
        # Loop through the nonce's
        time.time()
        for nonce in range(MAX_NONCE):
            # Find the correct hash to confirm a block
            text = str(block.get_block_number()) + str(transaction.to_string()) + str(self.get_previous_unconfirmed_hash()) + str(nonce)
            # Hash the text
            new_hash = hashlib.sha256(text.encode()).hexdigest()
            if new_hash.startswith(zeros):
                self.unconfirmed_blockchain.pop(0)
                self.confirm_block(transaction, new_hash)
                self.make_transaction(0, 0, "Mine reward", wallet_address, 50)
                print("Block mined: " + new_hash + " Nonce: " + str(nonce))
                return "x"

        return "Failed to mine block"

    def confirm_block(self, transaction, new_hash):
        """
        Add a mined block into the blockchain.
        :param blockchain: The blockchain.
        :param transaction: The transaction of the block.
        :param new_hash: The confirmed hash.
        """
        new_block = Block(transaction, self.get_previous_hash())
        new_block.set_hash(new_hash)
        self.add_block(new_block)

    def find_wallet(self, words, block_height):
        """
        Open an existing wallet from the blockchain.
        Using the public and private key and the block height that
        the wallet was created on.
        """
        mnemonics = Mnemonic("english")
        if mnemonics.check(words):
            seed = mnemonics.to_seed(words)
            entropy = mnemonics.to_entropy(words)
            public_key = self.generate_hash_byte(seed)
            private_key = self.generate_hash_byte(entropy)
            combined_keys = public_key + private_key
            compare_hash = self.generate_hash(combined_keys)
        else:
            return False

        if block_height > len(self.blockchain_list)-1:
            return False

        wallet_block = self.blockchain_list[block_height]

        if wallet_block.get_hash() == compare_hash:
            return True
        return False

    def get_wallet_information(self, words, block_height):
        """
        Get the full information about a wallet from the words and block height.
        :param words: The private mnemonics.
        :param block_height: Which block the wallet was created on.
        :return: Dictionary with private wallet information.
        """
        if self.find_wallet(words, block_height):
            mnemonics = Mnemonic("english")
            seed = mnemonics.to_seed(words)
            entropy = mnemonics.to_entropy(words)
            public_key = self.generate_hash_byte(seed)
            private_key = self.generate_hash_byte(entropy)
            combined_keys = public_key + private_key
            address = self.generate_hash(combined_keys)
            return {"public_key": public_key, "private_key": private_key, "words": words, "wallet_address": address, "block_height": block_height}
        return "WRONG"

    def get_blockchain(self):
        readable_blockchain = []
        # Convert all blocks into readable data
        for number, block in enumerate(self.blockchain_list):
            block_dict = {}
            block_dict["block_number"] = number
            block_dict["hash"] = block.get_hash()
            block_dict["previous_hash"] = block.get_previous_hash()
            block.set_block_number(number)
            readable_blockchain.append(block_dict)

        return readable_blockchain

    def get_unconfirmed_blockchain(self):
        readable_blockchain = []
        # Convert all blocks into readable data
        for number, block in enumerate(self.unconfirmed_blockchain):
            block_dict = {}
            block_dict["block_number"] = number
            block_dict["hash"] = block.get_hash()
            block_dict["previous_hash"] = block.get_previous_hash()
            block.set_block_number(number)
            readable_blockchain.append(block_dict)

        return readable_blockchain

    def print_blockchain(self):
        for number, block in enumerate(self.blockchain_list):
            block.set_block_number(number)
            print(
                '"""""""""""""""""""""""""""""""""""""""' + "\n" 
                '"" Block number: ' + str(number) + "\n"
                '"" Hash: ' + block.get_hash() + "\n"
                '"" Previous hash: ' + str(block.get_previous_hash()) + "\n"                                                
                '"""""""""""""""""""""""""""""""""""""""' + "\n"
            )

    def print_unconfirmed_blockchain(self):
        for number, block in enumerate(self.unconfirmed_blockchain):
            block.set_block_number(number)
            print(
                '"""""""""""""""""""""""""""""""""""""""' + "\n" 
                '"" Block number: ' + str(number) + "\n"
                '"" Hash: ' + block.get_hash() + "\n"
                '"" Previous hash: ' + str(block.get_previous_hash()) + "\n"                                                
                '"""""""""""""""""""""""""""""""""""""""' + "\n"
            )

    def get_previous_block(self):
        return self.blockchain_list[-1]

    def get_wallet_address(self, words, wallet_height):
        if self.find_wallet(words, wallet_height):
            mnemonics = Mnemonic("english")
            seed = mnemonics.to_seed(words)
            entropy = mnemonics.to_entropy(words)
            public_key = self.generate_hash_byte(seed)
            private_key = self.generate_hash_byte(entropy)
            combined_keys = public_key + private_key
            address = self.generate_hash(combined_keys)
            return address
        else:
            return "INVALID"

    def get_previous_hash(self):
        if len(self.blockchain_list) == 0:
            return 0
        block = self.blockchain_list[-1]
        return block.get_hash()

    def get_block_by_height(self, height):
        return self.blockchain_list[height]

    def get_previous_unconfirmed_block(self):
        return self.unconfirmed_blockchain[-1]

    def get_previous_unconfirmed_hash(self):
        if self.unconfirmed_blockchain == []:
            block = 0
        else:
            block = self.unconfirmed_blockchain[-1]

        if block == 0:
            return 0
        return block.get_hash()

    def get_unconfirmed_block_by_height(self, height):
        return self.unconfirmed_blockchain[height]

    def get_current_block_height(self):
        return len(self.blockchain_list) - 1


def test():
    blockchain = Blockchain()

    wallet = blockchain.create_node()
    wallet_2 = blockchain.create_node()
    wallet_address = wallet["wallet_address"]
    wallet2_address = wallet_2["wallet_address"]

    print(blockchain.print_blockchain())


