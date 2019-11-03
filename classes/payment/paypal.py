from classes.payment.payment import Payment
from models.paypal import Paypal

from flask import session
from flask_pymongo import PyMongo, wrappers
from database import mongo
from util import deserialize_json, json_result

class PayPal(Payment):
    def __init__(self):
        pass
    
    def purchase(self, paypal: Paypal, amount: int):
        if amount <= 0:
            return json_result(-1, "invalid amount")

        db:wrappers.Collection = mongo.db.paypal
        db.insert_one(paypal.__dict__)

        cdb: wrappers.Collection = mongo.db.credit
        result = cdb.find_one({ "username": session["username"] })
        if not result:
            result = {
                "username": session["username"],
                "credit": 0
            }
            cdb.insert_one(result)

        result["credit"] += amount
        cdb.update({ "username": session["username"] }, result)
        return json_result(0, "success")
    
    def history(self, username):
        db:wrappers.Collection = mongo.db.paypal
        return json_result(0, db.find({ "username": username }))