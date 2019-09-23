from classes.payment.payment import Payment
from models.coupon import Coupon as CouponModel

from flask_pymongo import PyMongo, wrappers
from database import mongo
from util import deserialize_json
import string, random

class Coupon(Payment):
    validch = [ ch for ch in list(string.ascii_uppercase + string.digits) ]

    def __init__(self):
        super()
    
    def generate(self):
        while True:
            gen = "".join([ random.choice(Coupon.validch) for _ in range(64) ])
            if self.__getCoupon(gen) == None:
                return gen
    
    def validate(self, coupon):
        for ch in coupon:
            if ch not in Coupon.validch:
                return False
    
        cm = self.__getCoupon(coupon)
        if cm == None:
            return False

        return True

    def get(self, username):
        db:wrappers.Collection = mongo.db.Coupons
        cm:list = deserialize_json(CouponModel, db.find({ "username": username }))
        if cm == None:
            return False
        return cm
      
    def use(self, username, coupon):
        db:wrappers.Collection = mongo.db.Coupons
        coupon:CouponModel = self.__getCoupon(coupon)
        if coupon == None:
            return False
        coupon.used = True
        db.update({ "username": username, "coupon": coupon }, coupon.__dict__)
        return True
    
    def __getCoupon(self, coupon):
        db:wrappers.Collection = mongo.db.Coupons
        cm:CouponModel = deserialize_json(CouponModel, db.find({ "coupon": coupon }))
        return cm

    def give(self, username, coupon):
        db:wrappers.Collection = mongo.db.Coupons
        if self.__getCoupon(coupon) == None:
            db.insert_one(CouponModel(username, coupon).__dict__)
            return True
        return False