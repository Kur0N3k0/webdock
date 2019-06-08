class Account(object):
    def __init__(self):
        pass



class PaymentInfo(object):
    def __init__(self, charge: int, account: Account):
        self.charge = charge
        self.account = account