class Paypal(object):
    def __init__(self,
        country_code,
        email,
        id,
        payer,
        username,
        amount,
        create_time,
        update_time
    ):
        self.contry_code = country_code
        self.email = email
        self.id = id
        self.payer = payer
        self.username = username
        self.amount = amount
        self.create_time = create_time
        self.update_time = update_time