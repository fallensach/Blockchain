from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

class CreateWalletForm(FlaskForm):
    submit = SubmitField("Generate wallet")

class OpenWalletForm(FlaskForm):
    mnemonics = StringField("Mnemonics")
    wallet_height = StringField("Block height")
    submit = SubmitField("Open wallet")

class SendTransactionForm(FlaskForm):
    wallet_address = StringField("Wallet address")
    receiver_address = StringField("Receiver's address")
    amount = StringField("Amount to send")
    send = SubmitField("Send transaction")

class MineForm(FlaskForm):
    mine = SubmitField("Mine")

class CloseWallet(FlaskForm):
    close = SubmitField("Close Wallet")