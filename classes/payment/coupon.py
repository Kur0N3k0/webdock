from classes.payment.payment import Payment
from models.coupon import Coupon as CouponModel

from flask_pymongo import PyMongo, wrappers
from database import mongo
from util import deserialize_json
import string, random, time

class Coupon(Payment):
    validch = [ ch for ch in list(string.ascii_uppercase + string.digits) ]

    def __init__(self):
        super()
    
    def all(self):
        db:wrappers.Collection = mongo.db.coupons
        cm:list = deserialize_json(CouponModel, db.find())
        return cm

    def generate(self):
        while True:
            gen = "".join([ random.choice(Coupon.validch) for _ in range(64) ])
            try:
                self.__getCoupon(gen).coupon
            except:
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
        db:wrappers.Collection = mongo.db.coupons
        cm:list = deserialize_json(CouponModel, db.find({ "username": username }))
        if cm == None:
            return False
        return cm
      
    def use(self, username, coupon):
        db:wrappers.Collection = mongo.db.coupons
        coupon:CouponModel = self.__getCoupon(coupon)
        if coupon == None or coupon.used == True:
            return False
        if self.__isexpired(coupon):
            return False
        coupon.used = True
        db.update({ "username": username, "coupon": coupon }, coupon.__dict__)
        return True
    
    def __getCoupon(self, coupon):
        db:wrappers.Collection = mongo.db.coupons
        cm:CouponModel = deserialize_json(CouponModel, db.find({ "coupon": coupon }))
        return cm

    def __isexpired(self, coupon_model: CouponModel):
        if coupon_model.expire_date >= time.time() + CouponModel.TERM:
            return True
        return False

    def give(self, username, coupon):
        db:wrappers.Collection = mongo.db.coupons
        db.insert_one(CouponModel(username, coupon).__dict__)
        return True
    
    def remove(self, username, coupon):
        db:wrappers.Collection = mongo.db.coupons
        db.delete_one({ "username": username, "coupon": coupon })
        return True