
class Room():
    def __init__(self, name, type, price, req, adminname):
        self.name = name
        self.type = type
        self.price = price
        self.req = req
        self.adminname = adminname
        self.isbooked = 0

    def set_properties(self, name, value):
        setattr(self, name, value)


class User():
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def set_properties(self, name, value):
        setattr(self, name, value)

class Booking():
    def __init__(self, bookingKey, rmname, type, price, req, adduserfecilitiese, startdate, enddate, loginusername):
        self.bookingKey = bookingKey
        self.rmname = rmname
        self.type = type
        self.price = price
        self.req = req
        self.adduserfecilitiese = adduserfecilitiese
        self.startdate = startdate
        self.enddate = enddate
        self.loginusername = loginusername

    def set_properties(self, name, value):
        setattr(self, name, value)
