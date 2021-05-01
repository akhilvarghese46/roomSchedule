
class Room():
    def __init__(self, name, type, price, req, adminname):
        self.name = name
        self.type = type
        self.price = price
        self.req = req
        self.adminname = adminname

    def set_properties(self, name, value):
        setattr(self, name, value)


class User():
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def set_properties(self, name, value):
        setattr(self, name, value)

class Booking():
    def __init__(self, name, type, price, req, startdate, enddate):
        self.name = name
        self.type = type
        self.price = price
        self.req = req
        self.startdate = startdate
        self.enddate = enddate

    def set_properties(self, name, value):
        setattr(self, name, value)
