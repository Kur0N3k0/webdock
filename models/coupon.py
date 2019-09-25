import uuid, time

class Coupon(object):
    TERM = 24 * 3600 * 30 * 2 # 2 month

    def __init__(self, username, coupon, used=False):
        self.username = username
        self.coupon = coupon
        self.used = used
        self.expire_date = time.time() + Coupon.TERM
        self.uuid = str(uuid.uuid4())