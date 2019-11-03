from models.account import Account
from flask_pymongo import PyMongo, wrappers
from database import mongo
import uuid

class Payment(object):
    def __init__(self):
        pass

    def purchase(self, price):
        raise "Payment::purchase not implemented"

    def deposit(self, amount):
        raise "Payment::deposit not implemented"
    
    def history(self):
        raise "Payment::history not implemented"
    
    def getCredit(self, username):
        db: wrappers.Collection = mongo.db.credit
        result = db.find_one({ "username": username })
        if not result:
            return 0
        return result["credit"]