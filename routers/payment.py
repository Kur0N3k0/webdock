import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from database import mongo
from classes.payment.payment import Payment

payment_api = Blueprint("payment_api", __name__)

@payment_api.route("/payment")
@payment_api.route("/payment/index")
def payment():
    return render_template("payment/index.html")

@payment_api.route("/payment/<int:ptype>")
def payment_set(ptype:int):
    if ptype == 0: # credit
        pass
    elif ptype == 1: # coupon
        pass
    elif ptype == 2: # paypal
        pass
    return render_template("payment/index.html")

@payment_api.route("/payment/credit")
@payment_api.route("/payment/credit/")
@payment_api.route("/payment/credit/list")
def payment_credit():
    return render_template("payment/index.html")

@payment_api.route("/payment/coupon/use")
def payment_credit_use():
    return render_template("payment/index.html")

@payment_api.route("/payment/coupon")
@payment_api.route("/payment/coupon/")
@payment_api.route("/payment/coupon/list")
def payment_coupon():
    return render_template("payment/index.html")

@payment_api.route("/payment/coupon/use")
def payment_coupon_use():
    return render_template("payment/index.html")

@payment_api.route("/payment/paypal")
@payment_api.route("/payment/paypal/")
@payment_api.route("/payment/paypal/list")
def payment_paypal():
    return render_template("payment/index.html")

@payment_api.route("/payment/paypal/use")
def payment_paypal_use():
    return render_template("payment/index.html")

