import uuid, json

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from database import mongo
from classes.payment.payment import Payment
from classes.payment.coupon import Coupon
from classes.payment.paypal import PayPal
from models.paypal import Paypal
from util import deserialize_json, login_required, json_result
from daemons import payment_daemon

payment_api = Blueprint("payment_api", __name__)
coupon_api = Coupon()
paypal_api = PayPal()
credit_api = Payment()
payment_daemon.start()

@payment_api.route("/payment")
@payment_api.route("/payment/index")
@login_required
def payment():
    credit = credit_api.getCredit(session["username"])
    return render_template("payment/index.html", credit=credit)

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

@payment_api.route("/payment/paypal/order", methods=["POST"])
@login_required
def payment_paypal_order():
    detail = request.form["details"]
    detail = json.loads(detail)

    create_time = detail["create_time"]
    update_time = detail["update_time"]
    tid = detail["id"]
    payer = detail["payer"]["payer_id"]
    country_code = detail["payer"]["address"]["country_code"]
    email = detail["payer"]["email_address"]
    username = session["username"]
    amount = int(detail["purchase_units"][0]["amount"]["value"])

    paypal = Paypal(
        country_code=country_code,
        email=email,
        id=tid,
        payer=payer,
        username=username,
        amount=amount,
        create_time=create_time,
        update_time=update_time
    )
    return paypal_api.purchase(paypal, amount)