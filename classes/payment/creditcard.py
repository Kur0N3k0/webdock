from classes.payment.payment import Payment
from models.account import Account
# from thirdparty.creditcard import Purchaser
# from database import mongo
# from flask_pymongo import PyMongo, wrappers

class CreditCard(Payment):
    def __init__(self, account: Account, cvv: int):
        if account.type != Account.CREDIT:
            raise "Account::type is not CreditCard"
        super(account)
        self.cvv = cvv
    
    def purchase(self, price):
        """
        purchaser = Purchaser(api_key)
        result = purchaser.request(self.account.account_num, self.cvv)
        if result == True:
            db: wrappers.Collection = mongo.db.payment
            db.insert_one(PaymentInfo(self.type, self.__dict__).__dict__)
            return True
        return False
        """
        pass

    def deposit(self, amount):
        raise "CreditCard is not implement deposit"
    
    def history(self):
        pass