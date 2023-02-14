from pathlib import Path
from flask import Flask, request, render_template, redirect, url_for
import os
from forms import CreateWalletForm, OpenWalletForm, SendTransactionForm, MineForm, CloseWallet
from blockchain import Blockchain

dir_path = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__, template_folder='templates')
app.static_folder = "static"
app.config["SECRET_KEY"] = "krypto"
blockchain = Blockchain()

app.debug = True

@app.route("/", methods=["GET", "POST"])
def start():
    form = OpenWalletForm()
    filename = Path("session.txt")
    if filename.exists():
        open(filename, "w").close()

    if form.is_submitted():
        result = request.form
        entered_wallet_information = {}
        for key in result.items():
                entered_wallet_information[key[0]] = key[1]

        if entered_wallet_information["wallet_height"] == "":
            return render_template("open_wallet.html", form=form)
        try:
            block_height = int(entered_wallet_information["wallet_height"])
        except:
            return render_template("open_wallet.html", form=form)

        words = entered_wallet_information["mnemonics"]

        if blockchain.find_wallet(words, block_height):
            wallet = blockchain.get_wallet_information(words, block_height)
            public_key = wallet["public_key"]
            private_key = wallet["private_key"]
            wallet_address = wallet["wallet_address"]
            balance = blockchain.get_wallet_balance(wallet_address)
            filename = Path("session.txt")
            filename.touch(exist_ok=True)
            file = open(filename, "w+")
            file.write(wallet_address + "\n" +
                       public_key + "\n" +
                       private_key
                       )
            file.close()
            return render_template("wallet.html", public_key=public_key, private_key=private_key, words=words,wallet_address=wallet_address, balance=balance, block_height=block_height)

    return render_template("open_wallet.html", form=form)


# Creates a new wallet
@app.route("/create_wallet", methods=["GET", "POST"])
def create_wallet():
    form = CreateWalletForm()
    if form.is_submitted():
        wallet = blockchain.create_node()
        public_key = wallet["public_key"]
        wallet_address = wallet["wallet_address"]
        private_key = wallet["private_key"]
        words = wallet["words"]
        balance = blockchain.get_wallet_balance(wallet_address)
        block_height = wallet["block_height"]
        return render_template("save_wallet.html", wallet_address=wallet_address, public_key=public_key, private_key=private_key, words=words, balance=balance, block_height=block_height)

    return render_template("create_wallet.html", form=form)



@app.route("/home", methods=["GET", "POST"])
def home():
    open_wallet_form = OpenWalletForm()
    wallet_keys = {}
    filename = Path("session.txt")
    if filename.exists():
        file = open(filename, "r")
        if not is_wallet_open():
            return redirect(url_for("start"))

        keys = file.readlines()
        for index, key in enumerate(keys):
            key = key.strip()
            if index == 0:
                wallet_keys["wallet_address"] = key
            elif index == 1:
                wallet_keys["public_key"] = key
            elif index == 2:
                wallet_keys["private_key"] = key
        file.close()

    else:
        return render_template("open_wallet.html", form=open_wallet_form)

    close_form = CloseWallet()
    confirmed_transactions = blockchain.get_confirmed_transactions(wallet_keys["wallet_address"])
    unconfirmed_transactions = blockchain.get_unconfirmed_transactions(wallet_keys["wallet_address"])

    if close_form.is_submitted():
        return redirect(url_for("start"))

    return render_template("home.html", wallet_address=wallet_keys["wallet_address"], close_form=close_form, confirmed_transactions=confirmed_transactions, unconfirmed_transactions=unconfirmed_transactions)



@app.route("/transaction", methods=["GET", "POST"])
def transaction():
    open_wallet_form = OpenWalletForm()
    wallet_keys = {}
    filename = Path("session.txt")
    if filename.exists():
        file = open(filename, "r")
        if not is_wallet_open():
            return redirect(url_for("start"))

        keys = file.readlines()
        for index, key in enumerate(keys):
            key = key.strip()
            if index == 0:
                wallet_keys["wallet_address"] = key
            elif index == 1:
                wallet_keys["public_key"] = key
            elif index == 2:
                wallet_keys["private_key"] = key
        file.close()

    else:
        return render_template("open_wallet.html", form=open_wallet_form)

    form = SendTransactionForm()
    if form.is_submitted() and "send" in request.form:
        transaction_data = request.form
        receiver = transaction_data.get("receiver_address")
        amount = transaction_data.get("amount")
        blockchain.make_transaction(wallet_keys["private_key"], wallet_keys["public_key"],
                                    wallet_keys["wallet_address"], receiver, amount)
    balance = blockchain.get_wallet_balance(wallet_keys["wallet_address"])
    return render_template("transaction.html", form=form, balance=balance)


@app.route("/mine", methods=["GET", "POST"])
def mine():
    unconfirmed_blockchain = blockchain.get_unconfirmed_blockchain()
    print(unconfirmed_blockchain)
    open_wallet_form = OpenWalletForm()
    wallet_keys = {}
    filename = Path("session.txt")
    if filename.exists():
        file = open(filename, "r")
        if not is_wallet_open():
            return redirect(url_for("start"))

        keys = file.readlines()
        for index, key in enumerate(keys):
            key = key.strip()
            if index == 0:
                wallet_keys["wallet_address"] = key
            elif index == 1:
                wallet_keys["public_key"] = key
            elif index == 2:
                wallet_keys["private_key"] = key
        file.close()

    else:
        return render_template("open_wallet.html", form=open_wallet_form)

    mine = MineForm()
    if mine.is_submitted() and "mine" in request.form:
        blockchain.mine_oldest_block(wallet_keys["wallet_address"])
        return redirect("mine")

    return render_template("mine.html", mine_form=mine,  unconfirmed_blockchain=unconfirmed_blockchain)



@app.route("/blockchain", methods=["GET", "POST"])
def view_blockchain():
    confirmed_blockchain = blockchain.get_blockchain()
    wallet_keys = {}

    mine = MineForm()
    if mine.is_submitted() and "mine" in request.form:
        blockchain.mine_oldest_block(wallet_keys["wallet_address"])

    return render_template("blockchain.html", blockchain=confirmed_blockchain)

@app.route("/wallet", methods=["GET"])
def wallet():
    return render_template("wallet.html")

def is_wallet_open():
    filename = Path("session.txt")
    if filename.exists():
        file = open(filename, "r")
        if not file.read(1):
            return False
    return True

if __name__ == "__main__":
    app.debug = True
    app.run()

