import uuid

class Payment(object):
    NO = 0
    CREDIT_CARD = 1

    def __init__(self, ptype: int, info: dict, _uuid: uuid.UUID):
        self.ptype = ptype
        self.info = info
        self.uuid = _uuid
    
    def purchase(self, price):
        raise "Payment::purchase not implemented"

    def deposit(self, amount):
        raise "Payment::deposit not implemented"
    
    def history(self):
        raise "Payment::history not implemented"
    