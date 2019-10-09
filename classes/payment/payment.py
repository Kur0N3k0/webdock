from models.account import Account
import uuid

class Payment(object):
    def __init__(self, account):
        self.account: Account = account

    def purchase(self, price):
        raise "Payment::purchase not implemented"

    def deposit(self, amount):
        raise "Payment::deposit not implemented"
    
    def history(self):
        raise "Payment::history not implemented"
    