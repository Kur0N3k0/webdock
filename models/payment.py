import uuid

class Payment(object):
    NO = 0
    CREDIT_CARD = 1

    def __init__(self, ptype: int, info: dict, _uuid: uuid.UUID):
        self.ptype = ptype
        self.info = info
        self.uuid = _uuid
    
    def purchase(self, price):
        pass

    def deposit(self, amount):
        pass
    
    def history(self):
        pass
    