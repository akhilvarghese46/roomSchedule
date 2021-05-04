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
    return name_list

def getBookingRoomFilter(bookData):
    name_list = []
    query = datastore_client.query(kind="Room").fetch()
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

        return render_template("add_room.html")
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

@app.route("/addroombookingSearch", methods=["GET", "POST"])
def getRoomBookingSearch():

    return render_template("search_booking.html")

@app.route("/addRoomBookSearchResult", methods=["GET", "POST"])
def getRoomBookingSearchResult():
    user_data =checkUserData();
    if user_data != None:
        try:
            data = dict(request.form)
            fromDate = data.get("fromDate")
            toDate = data.get("toDate")
            rmType  = data.get("roomType")
            booking={}
            booking["fromDate"] = fromDate
            booking["toDate"] = toDate
            booking["rmType"] = rmType
            name_list = getBookingRoomFilter(booking)
            return render_template("search_bookinglist.html",booking=booking ,avlRoom = name_list)
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
            name=roomData["name"]
            entity_key = datastore_client.key("BookingRoomList", name)
            entity = datastore.Entity(key=entity_key)
            booking = Booking(rmname= name, type = roomData["type"], price=roomData["price"], req = roomData["req"],adduserfecilitiese=data.get("addUserReq"), startdate =booking['fromDate'], enddate=booking['toDate'], loginusername = user_data['email'])
            entity.update(booking.__dict__)
            datastore_client.put(entity)
            return render_template("search_booking.html")
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
