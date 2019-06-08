from models.payment import Payment

class User(object):
    name = None
    password = None
    payment = None
    uuid = None

    def __init__(self, name: str, password: str, payment: Payment, charge: int, uuid: uuid):
        self.name = name
        self.password = password
        self.payment = payment
        self.uuid = uuid