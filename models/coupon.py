import uuid, time

class Coupon(object):
    def __init__(self, username, coupon, used=False):
        self.username = username
        self.coupon = coupon
        self.used = used
        self.expire_date = time.time() + 24*3600*30 * 2 # 2 month
        self.uuid = str(uuid.uuid4())