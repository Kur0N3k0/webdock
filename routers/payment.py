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
    uid = session["uuid"]
    
    

    return ""