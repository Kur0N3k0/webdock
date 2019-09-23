class Coupon(object):
    def __init__(self, username, coupon, used=0):
        self.username = username
        self.coupon = coupon
        self.used = used