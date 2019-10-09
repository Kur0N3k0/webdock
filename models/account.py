class Account(object):
    CREDIT = 0
    PAYPAL = 1
    TYPE = [ CREDIT, PAYPAL ]
    def __init__(self, username, account_num, atype):
        self.username = username
        self.account_num = account_num
        self.type = atype