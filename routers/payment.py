import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from database import mongo
from classes.payment.payment import Payment
from classes.payment.coupon import Coupon
from classes.payment.creditcard import CreditCard
from util import deserialize_json, login_required, json_result
from daemons import payment_daemon

payment_api = Blueprint("payment_api", __name__)
coupon_api = Coupon()
payment_daemon.start()

@payment_api.route("/payment")
@payment_api.route("/payment/index")
@login_required
def payment():
    return render_template("payment/index.html")

@payment_api.route("/payment/credit")
@payment_api.route("/payment/credit/")
@payment_api.route("/payment/credit/list")
@login_required
def payment_credit():
    return render_template("payment/index.html")

@payment_api.route("/payment/coupon/use")
@login_required
def payment_credit_use():
    return render_template("payment/index.html")

@payment_api.route("/payment/coupon")
@payment_api.route("/payment/coupon/")
@payment_api.route("/payment/coupon/list")
@login_required
def payment_coupon():
    coupons = coupon_api.get(session["username"])
    r = [ c.used for c in coupons ]
    used_cnt = r.count(True)
    noused_cnt = r.count(False)
    return render_template(
        "payment/coupon-list.html",
        coupons=coupons,
        used_cnt=used_cnt,
        noused_cnt=noused_cnt
    )

@payment_api.route("/payment/coupon/use")
@login_required
def payment_coupon_use():
    coupon = request.form["coupon"]
    if coupon_api.use(session["username"], coupon):
        return json_result(0, "success")
    return json_result(-1, "coupon not exist")

@payment_api.route("/payment/paypal")
@payment_api.route("/payment/paypal/")
@payment_api.route("/payment/paypal/list")
@login_required
def payment_paypal():
    return render_template("payment/index.html")

@payment_api.route("/payment/paypal/use")
@login_required
def payment_paypal_use():
    return render_template("payment/index.html")

