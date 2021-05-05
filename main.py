from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
import google.oauth2.id_token
from datetime import datetime
import random
from google.cloud import datastore
import json
from models import Room,Booking

app = Flask(__name__)
datastore_client = datastore.Client()
firebase_request_adapter = requests.Request()

def checkUserData():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    addresses = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,firebase_request_adapter)
        except ValueError as exc:
            return render_template("error.html", error_message=str(exc))
    return claims

def getAvailableRoomData():
    name_list = []
    query = datastore_client.query(kind="Room")
    query = query.add_filter('isbooked', '=', 0).fetch()
    for i in query:
        name_list.append(dict(i))
        print(dict(i))
    return name_list
    """query_2 = datastore_client.query(kind="BookingRoomList").fetch()
    for i in query:
        name_list.append(dict(i))
    return name_list"""


def getBookedRoomListDetails():
    name_list = []
    query = datastore_client.query(kind="BookingRoomList").fetch()
    for i in query:
        name_list.append(dict(i))
    return name_list

def getBookingRoomFilter(bookData):
    fromDate=datetime.fromisoformat(bookData['fromDate'])
    toDate=datetime.fromisoformat(bookData['toDate'])
    name_list = []
    query = datastore_client.query(kind="Room")
    query = query.add_filter('type', '=', bookData["rmType"]).fetch()
    for i in query:
        data = dict(i)
        data["isBooked"] = 0
        data["fromDate"] = None
        data["toDate"] = None
        query_2 = datastore_client.query(kind="BookingRoomList")
        query_2 = query_2.add_filter('rmname', '=', dict(i)['name']).fetch()
        for j in query_2:
            if(dict(i)['name'] == dict(j)['rmname']):
                data["isBooked"] = 1
                data["fromDate"] = dict(j)['startdate']
                data["toDate"] = dict(j)['enddate']
        name_list.append(data)
        newname_list =[]
        for data in name_list:
            if(data['fromDate']!=None and data['toDate']!=None):
                if((fromDate >=datetime.fromisoformat(data['fromDate']) and toDate <= datetime.fromisoformat(data['toDate']) and fromDate >=datetime.fromisoformat(data['toDate'])) or (fromDate >=datetime.fromisoformat(data['fromDate']) and toDate >= datetime.fromisoformat(data['toDate']) and fromDate >=datetime.fromisoformat(data['toDate'])) or (fromDate <= datetime.fromisoformat(data['fromDate']) and toDate <= datetime.fromisoformat(data['toDate']) and datetime.fromisoformat(data['fromDate'])>=toDate )):
                    newname_list.append(data)
            else:
                newname_list.append(data)
    return name_list

def getBookedRoomDetails(bookingId):
    name_list = []
    query = datastore_client.query(kind="BookingRoomList")
    query = query.add_filter('bookingKey', '=', bookingId).fetch()
    for i in query:
        name_list.append(dict(i))
    return name_list

def getRoomDetails(rmname):
    entity_key = datastore_client.key("Room", rmname)
    enitity_exists = datastore_client.get(key=entity_key)
    if enitity_exists:
        enitity_exists = dict(enitity_exists)
        enitity_exists["name"] = rmname
    else:
        return render_template("error.html", error_message="No data found")
    return enitity_exists

#root function is a default function
@app.route('/')
def root():
    user_data =checkUserData();
    if user_data == None:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)
    else:
        name_list = getAvailableRoomData();
        return render_template("main.html", user_data=user_data,rooms=name_list)

@app.route("/addroom", methods=["GET", "POST"])
def setRoomDetails():
    user_data =checkUserData();
    if user_data != None:
        """ create room entry"""
        data = dict(request.form)
        name = data.get("rmName")
        if name:
            entity_key = datastore_client.key("Room", name)
            enitity_exists = datastore_client.get(key=entity_key)
            if not enitity_exists:
                """create the room if an entry with name not exists"""
                entity = datastore.Entity(key=entity_key)
                data.pop("rmName")
                room = Room(name= name, type = data.get("roomType"), price=data.get("rmPrice"), req = data.get("addReq"), adminname = user_data['email'])
                entity.update(room.__dict__)
                datastore_client.put(entity)
            else:
                error_message = "an entry with same name already exists. try with an another name"
                return render_template("error.html", error_message=error_message)
        return render_template("add_room.html",user_data=user_data)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/availableroomlist", methods=["GET", "POST"])
def getAvailableRoomList():
    user_data =checkUserData();
    if user_data != None:
        try:
            name_list = getAvailableRoomData();
            return render_template("available_roomlist.html", user_data=user_data, rooms=name_list)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/availableroomdetails/<name>", methods=["GET", "POST"])
def getAvailableRoomDetails(name=None):
    user_data =checkUserData();
    if user_data != None:
        try:
            if name:
                entity_key = datastore_client.key("Room", name)
                enitity_exists = datastore_client.get(key=entity_key)
                if enitity_exists:
                    enitity_exists = dict(enitity_exists)
                    enitity_exists["name"] = name
                    return render_template("available_roomdetails.html", data=enitity_exists)
                else:
                    return render_template("error.html", error_message="No data found")
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/editavailableroom/<name>", methods=["GET", "POST"])
def editAvailableRoom(name=None):
    user_data =checkUserData();
    if user_data != None:
        try:
            if name:
                entity_key = datastore_client.key("Room", name)
                enitity_exists = datastore_client.get(key=entity_key)
                if enitity_exists:
                    enitity_exists = dict(enitity_exists)
                    enitity_exists["name"] = name
                    if request.method == "GET":
                        return render_template("edit_room.html", data=enitity_exists)
                    else:
                        try:
                            data = dict(request.form)
                            print(data)
                            entity = datastore.Entity(key=entity_key)
                            room = Room(name=name, type=data.get("roomType"), price=data.get("rmPrice"), req=data.get("addReq"),adminname = user_data['email'])
                            obj = room.__dict__
                            obj.pop("name")
                            entity.update(obj)
                            datastore_client.put(entity)
                            obj["name"] = name
                            return render_template("available_roomdetails.html", data=obj)

                        except Exception as e:
                            print(e)
                            return render_template("error.html", error_message=str(e))
            return render_template("edit_room.html")
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)


@app.route("/addroombookingSearch", methods=["GET", "POST"])
def getRoomBookingSearch():
    startdate=datetime.today().strftime('%d-%m-%y')
    return render_template("search_booking.html",startdate=startdate)

@app.route("/addRoomBookSearchResult", methods=["GET", "POST"])
def getRoomBookingSearchResult():
    user_data =checkUserData();
    if user_data != None:
        try:
            data = dict(request.form)
            startDate = data.get("fromDate")
            endDate = data.get("toDate")
            rmType  = data.get("roomType")
            todayDate = datetime.today()
            fromDate=datetime.fromisoformat(startDate)
            print(fromDate)
            if(todayDate > fromDate):
                error_message = "User can't select previous dates as checkin date"
                return render_template("error.html", error_message=error_message)
            booking={}
            booking["fromDate"] = startDate
            booking["toDate"] = endDate
            booking["rmType"] = rmType
            name_list = getBookingRoomFilter(booking)

            return render_template("search_bookinglist.html",booking=booking ,avlRoom = name_list,user_data=user_data)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/addRoomBook", methods=["GET", "POST"])
def setRoomBooking():
    rmname = request.args.get('room')
    booking = request.args.get('booking')
    booking = booking.replace("'", "\"")
    booking=json.loads(booking)
    booking["rmname"] = rmname
    if rmname:
        name_list = getRoomDetails(rmname)
        return render_template("add_booking.html" ,roomData = name_list,booking=booking)
    else:
        return render_template("search_booking.html")

@app.route("/addRoomBookToDb", methods=["GET", "POST"])
def addRoomBookToDb():
    user_data =checkUserData();
    if user_data != None:
        try:
            data = dict(request.form)
            bookingdata = data.get("booking")
            bookingdata = bookingdata.replace("'", "\"")
            booking=json.loads(bookingdata)
            roomData = data.get("roomData")
            roomData = roomData.replace("'", "\"")
            roomData=json.loads(roomData)
            name =roomData["name"]
            bookingKey = name+"|"+booking['fromDate']+"|"+booking['toDate']+"|"+user_data['email']
            entity_key = datastore_client.key("BookingRoomList",bookingKey)
            entity = datastore.Entity(key=entity_key)
            booking = Booking(bookingKey=bookingKey, rmname= name, type = roomData["type"], price=roomData["price"], req = roomData["req"],adduserfecilitiese=data.get("addUserReq"), startdate =booking['fromDate'], enddate=booking['toDate'], loginusername = user_data['email'])
            entity.update(booking.__dict__)
            datastore_client.put(entity)
            return render_template("search_booking.html")
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)

@app.route("/bookedroomlist", methods=["GET", "POST"])
def getBookedRoomList():
    user_data =checkUserData();
    if user_data != None:
        try:
            name_list=getBookedRoomListDetails();
            return render_template("bookedroomlist.html" ,userdata=user_data, BookedRoomData=name_list)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)

@app.route("/updatebookederoom/<bookingId>", methods=["GET", "POST"])
def updateBookedRoom(bookingId=None):
    user_data =checkUserData();
    print("-----------------------1-----------------------------")
    print(request.method)
    if user_data != None:
        print("-----------------------2-----------------------------")

        try:
            data = dict(request.form)
            bookingdata = data.get("bookedRmData")
            bookingdata = bookingdata.replace("'", "\"")
            booking=json.loads(bookingdata)
            oldstartdate = booking['startdate']
            oldtodate = booking['enddate']
            if((oldstartdate != data.get("fromDate")) or (oldtodate!= data.get("toDate")) ):
                print("-----------------------5-----------------------------")

                bookingKey = booking['rmname']+"|"+data.get("fromDate")+"|"+data.get("toDate")+"|"+user_data['email']
                entity_key = datastore_client.key("BookingRoomList", bookingKey)
                enitity_exists = datastore_client.get(key=entity_key)
                if enitity_exists:
                    error_message = "an entry with same name already exists. try with an another name"
                    return render_template("error.html", error_message=error_message)
                else:
                    entity_key_old = datastore_client.key("BookingRoomList", bookingKey)
                    datastore_client.delete(key=entity_key_old)
            entity = datastore.Entity(key=bookingKey)
            bookingObj = Booking(bookingKey=bookingKey, rmname= booking['rmname'], type = booking["type"], price=booking["price"], req = data.get("roomType"),adduserfecilitiese=booking['req'], startdate =data.get("fromDate"), enddate=data.get("toDate"), loginusername = user_data['email'])
            obj = bookingObj.__dict__
            obj.pop("bookingKey")
            entity.update(obj)
            datastore_client.put(entity)
            name_list=getBookedRoomListDetails();
            return render_template("bookedroomlist.html" ,userdata=user_data, BookedRoomData=name_list)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)

@app.route("/editbookederoom/<bookingId>", methods=["GET", "POST"])
def editBookedRoom(bookingId=None):
    user_data =checkUserData();
    print("-----------------------1-----------------------------")
    print(request.method)
    if user_data != None:
        print("-----------------------2-----------------------------")
        try:
            if bookingId:
                print("-----------------------3-----------------------------")

                name_list = getBookedRoomDetails(bookingId)
                return render_template("edit_booking.html",user_data=user_data,bookedRmData=name_list)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)

@app.route("/deletebookederoom/<id>", methods=["GET", "POST"])
def deleteBookedRoom(id=None):
    user_data =checkUserData();
    if user_data != None:
        try:
            if id != None:
                name_list = []
                entity_key = datastore_client.key("BookingRoomList", id)
                datastore_client.delete(key=entity_key)
                name_list=getBookedRoomListDetails();
                return render_template("bookedroomlist.html", user_data=user_data, BookedRoomData=name_list)
            else:
                error_message = "Page not loaded! User Data is missing"
                return render_template("error.html", error_message=error_message)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)

@app.route("/singnout", methods=["GET", "POST"])
def signOut():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
