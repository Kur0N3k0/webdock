class Token(object):
    def __init__(self, tenant, expire_date, token):
        self.tenant = tenant
        self.expire_date = expire_date
        self.token = token