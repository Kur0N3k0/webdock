from models.paymentinfo import PaymentInfo

class Payment(object):
    ptype = ""
    info = None
    uuid = ""

    def __init__(self, ptype: int, info: PaymentInfo, uuid: uuid):
        self.ptype = ptype
        self.info = info
        self.uuid = uuid
    
    def purchase(self, price):
        pass

    def deposit(self, amount):
        pass
    