from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
import google.oauth2.id_token
from datetime import datetime
import random
from google.cloud import datastore
import json
from models import Room,Booking,User

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
    """query_2 = datastore_client.query(kind="BookingRoomList").fetch()
    for i in query:
        name_list.append(dict(i))
    return name_list"""


def getBookedRoomListDetails(bookingSearch):
    name_list = []
    if (bookingSearch):
        if(bookingSearch['rmType'] == 'AllType'):
            query = datastore_client.query(kind="BookingRoomList").fetch()
        else:
            query = datastore_client.query(kind="BookingRoomList")
            query = query.add_filter('type', '=', bookingSearch['rmType']).fetch()
    else:
        query = datastore_client.query(kind="BookingRoomList").fetch()
    for i in query:
        name_list.append(dict(i))
    return name_list

def getBookingRoomFilter(bookData):
    fromDate=datetime.fromisoformat(bookData['fromDate'])
    toDate=datetime.fromisoformat(bookData['toDate'])
    name_list = []
    newname_list =[]
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

        for data in name_list:
            if(data['fromDate']!=None and data['toDate']!=None):
                if((fromDate >=datetime.fromisoformat(data['fromDate']) and toDate <= datetime.fromisoformat(data['toDate']) and fromDate >=datetime.fromisoformat(data['toDate'])) or (fromDate >=datetime.fromisoformat(data['fromDate']) and toDate >= datetime.fromisoformat(data['toDate']) and fromDate >=datetime.fromisoformat(data['toDate'])) or (fromDate <= datetime.fromisoformat(data['fromDate']) and toDate <= datetime.fromisoformat(data['toDate']) and datetime.fromisoformat(data['fromDate'])>=toDate )):
                    newname_list.append(data)
            else:
                newname_list.append(data)
    return newname_list

def getBookingRoomFilterTwo(bookData):
    fromDate=datetime.fromisoformat(bookData['fromDate'])
    toDate=datetime.fromisoformat(bookData['toDate'])
    name_list = []
    query = datastore_client.query(kind="Room")
    query = query.add_filter('name', '=', bookData["rmName"]).fetch()
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
    return newname_list


def getBookedRoomDetails(bookingId):
    name_list = []
    query = datastore_client.query(kind="BookingRoomList")
    query = query.add_filter('bookingKey', '=', bookingId).fetch()
    for i in query:
        name_list.append(dict(i))
    return name_list

def getBookedRoomDetailsData():
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

def getUserDetails(bookingId):
    entity_key = datastore_client.key("UserDetails", bookingId)
    enitity_exists = datastore_client.get(key=entity_key)
    if enitity_exists:
        enitity_exists = dict(enitity_exists)
        enitity_exists["bookingId"] = bookingId
    else:
        return render_template("error.html", error_message="No data found")
    return enitity_exists

def addUserDetails(userDetails):
    entity_key = datastore_client.key("UserDetails", userDetails["bookingKey"])
    entity = datastore.Entity(key=entity_key)
    userDetails = User(username=userDetails["userName"], email=userDetails["userEmail"], age=userDetails["userAge"], contactnum=userDetails["userNumber"], gender=userDetails["userGender"], bookingId=userDetails["bookingKey"])
    entity.update(userDetails.__dict__)
    datastore_client.put(entity)

def updateUserDetails(userDetails):
    entity_key = datastore_client.key("UserDetails", userDetails["bookingKey"])
    entity = datastore.Entity(key=entity_key)
    userDetails = User(username=userDetails["userName"], email=userDetails["userEmail"], age=userDetails["userAge"], contactnum=userDetails["userNumber"], gender=userDetails["userGender"], bookingId=userDetails["bookingKey"])
    obj = userDetails.__dict__
    entity.update(obj)
    datastore_client.put(entity)

#root function is a default function
@app.route('/')
def root():
    user_data =checkUserData();
    if user_data == None:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)
    else:
        name_list = getAvailableRoomData();
        todayDate= datetime.today().strftime('%Y-%m-%d')
        return render_template("main.html", user_data=user_data,rooms=name_list,todayDate=todayDate)

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
                            editedname =str(data.get("rmname")).upper();
                            oldname =str(data.get("oldrmname")).upper();
                            if(editedname != oldname ):
                                entity_key = datastore_client.key("Room", editedname)
                                newenitity_exists = datastore_client.get(key=entity_key)
                                if newenitity_exists:
                                    error_message = "An entry with same name already exists. try with an another name"
                                    return render_template("error.html", error_message=error_message)
                                else:
                                    entity_key_old = datastore_client.key("Room", name)
                                    datastore_client.delete(key=entity_key_old)
                            entity = datastore.Entity(key=entity_key)
                            room = Room(name=editedname, type=data.get("roomType"), price=data.get("rmPrice"), req=data.get("addReq"),adminname = user_data['email'])
                            obj = room.__dict__

                            entity.update(obj)
                            datastore_client.put(entity)
                            obj["name"] = editedname
                            return render_template("available_roomdetails.html", data=obj)

                        except Exception as e:

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
    user_data =checkUserData()
    if user_data != None:
        try:
            startdate=datetime.today().strftime('%d-%m-%y')
            name_list = getBookedRoomDetailsData()
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)
    return render_template("search_bookinglist.html",user_data=user_data,startdate=startdate,avlRoom=name_list)

@app.route("/addRoomBookSearchResult", methods=["GET", "POST"])
def getRoomBookingSearchResult():
    user_data =checkUserData();
    if user_data != None:
        try:
            data = dict(request.form)
            startDate = data.get("fromDate")
            endDate = data.get("toDate")
            rmType  = data.get("roomType")
            rmname = data.get("rmname")
            bookingDataUrl = data.get("booking")
            bookingDataUrl = bookingDataUrl.replace("'", "\"")
            bookingDataUrl=json.loads(bookingDataUrl)
            todayDate = datetime.today()
            fromDate=datetime.fromisoformat(startDate)
            ToDate=datetime.fromisoformat(endDate)
            if(ToDate < fromDate):
                return_url = '/addroombookingSearch'
                error_message = "Check-in date should be less than Check-out Date"
                return render_template("error.html", error_message=error_message,return_url=return_url)
            if(todayDate > fromDate):
                return_url = '/addroombookingSearch'
                error_message = "User can't select previous dates as checkin date"
                return render_template("error.html", error_message=error_message,return_url=return_url)
            booking={}
            booking["fromDate"] = startDate
            booking["toDate"] = endDate
            booking["rmType"] = rmType
            booking["rmName"] = rmname
            name_list = getBookingRoomFilterTwo(booking)

            if name_list:
                booking["rmPrice"] =name_list[0]["price"]
                booking["req"] =name_list[0]["req"]
                return render_template("add_booking.html" ,user_data=user_data,roomData = name_list[0],booking=booking)
            else:
                return_url = '/addroombookingSearch'
                error_message = "An entry with same date is already exists. try with an another date/time"
                return render_template("error.html", error_message=error_message,return_url=return_url)

            """return render_template("search_bookinglist.html",booking=booking ,avlRoom = name_list,user_data=user_data)"""
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)

@app.route("/addRoomBook", methods=["GET", "POST"])
def setRoomBooking():
    rmname = request.args.get('room')
    rmname = request.args.get('room')
    booking = request.args.get('booking')
    booking = booking.replace("'", "\"")
    booking=json.loads(booking)
    booking["rmname"] = rmname
    """if rmname:
        name_list = getRoomDetails(rmname)
        return render_template("add_booking.html" ,roomData = name_list,booking=booking)
    else:"""
    return render_template("search_booking.html",rmname=rmname,booking=booking)


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

            """roomData = roomData.replace("'", "\"")
            roomData = roomData.replace('\r\n', '\\r\\n')
            roomData=json.loads(roomData)
            """

            userDetails={}
            userDetails["userName"] = data.get("userName")
            userDetails["userAge"] = data.get("userAge")
            userDetails["userNumber"] = data.get("userNumber")
            userDetails["userGender"] = data.get("userGender")
            userDetails["userEmail"] = user_data['email']

            name =booking["rmName"]
            bookingKey = name+"|"+booking['fromDate']+"|"+booking['toDate']+"|"+user_data['email']
            userDetails["bookingKey"] = bookingKey
            entity_key = datastore_client.key("BookingRoomList",bookingKey)
            entity = datastore.Entity(key=entity_key)
            booking = Booking(bookingKey=bookingKey, rmname= name, type = booking["rmType"], price=booking["rmPrice"], req = booking["req"],adduserfecilitiese=data.get("addUserReq"), startdate =booking['fromDate'], enddate=booking['toDate'], loginusername = user_data['email'])
            entity.update(booking.__dict__)
            datastore_client.put(entity)
            name_list = getBookedRoomDetailsData()
            addUserDetails(userDetails)
            return render_template("search_bookinglist.html" ,avlRoom=name_list)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)

@app.route("/bookedroomlist/<type>", methods=["GET", "POST"])
def getBookedRoomList(type):
    user_data =checkUserData();
    if user_data != None:
        try:
            bookingSearch={}
            bookingSearch["rmType"] = type
            data = dict(request.form)
            if(data.get("roomType") != 'AllType' and data.get("roomType") != None):
                bookingSearch["rmType"] = data.get("roomType")
            name_list=getBookedRoomListDetails(bookingSearch);
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
    if user_data != None:
        try:
            data = dict(request.form)
            bookingdata = data.get("bookedRmData")
            bookingdata = bookingdata.replace("'", "\"")
            booking=json.loads(bookingdata)
            oldstartdate = booking['startdate']
            oldtodate = booking['enddate']

            bookingOldDataId = data.get("bookingOldDataId")
            if(bookingOldDataId != "novalue"):
                entity_key_old = datastore_client.key("BookingRoomList", bookingOldDataId)
                datastore_client.delete(key=entity_key_old)

            """
            if((oldstartdate != data.get("fromDate")) or (oldtodate!= data.get("toDate")) ):
                bookingKey = booking['rmname']+"|"+data.get("fromDate")+"|"+data.get("toDate")+"|"+user_data['email']
                entity_key = datastore_client.key("BookingRoomList", bookingKey)
                enitity_exists = datastore_client.get(key=entity_key)
                if enitity_exists:
                    error_message = "an entry with same name already exists. try with an another name"
                    return render_template("error.html", error_message=error_message)
                else:
                    entity_key_old = datastore_client.key("BookingRoomList", bookingKey)
                    datastore_client.delete(key=entity_key_old)
                    """
            userDetails={}
            userDetails["userName"] = data.get("userName")
            userDetails["userAge"] = data.get("userAge")
            userDetails["userNumber"] = data.get("userNumber")
            userDetails["userGender"] = data.get("userGender")
            userDetails["userEmail"] = user_data['email']
            bookingId = booking['bookingKey']
            if (booking['bookingKey']== 'nobookingid'):
                bookingId = booking['rmname']+"|"+booking['startdate']+"|"+booking['enddate']+"|"+user_data['email']
            userDetails["bookingKey"] = bookingId
            updateUserDetails(userDetails)
            entity_key = datastore_client.key("BookingRoomList", bookingId)
            entity = datastore.Entity(key=entity_key)
            bookingObj = Booking(bookingKey=bookingId, rmname= booking['rmname'], type = booking["type"], price=booking["price"], req = booking['req'],adduserfecilitiese=data.get("addReq"), startdate =booking['startdate'], enddate=booking['enddate'], loginusername = user_data['email'])
            obj = bookingObj.__dict__

            entity.update(obj)
            datastore_client.put(entity)
            bookingSearch={}
            name_list=getBookedRoomListDetails(bookingSearch);
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
    if user_data != None:
        try:
            if bookingId:
                name_list = getBookedRoomDetails(bookingId)
                return render_template("edit_search_booking.html",user_data=user_data,bookedRmData=name_list)
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
                bookingSearch={}
                name_list=getBookedRoomListDetails(bookingSearch);
                return render_template("bookedroomlist.html", userdata=user_data, BookedRoomData=name_list)
            else:
                error_message = "Page not loaded! User Data is missing"
                return render_template("error.html", error_message=error_message)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)

@app.route("/deleteavailableroom/<id>", methods=["GET", "POST"])
def deleteavailableroom(id=None):
    user_data =checkUserData();
    if user_data != None:
        try:
            if id != None:
                name_list =[]
                entity_key = datastore_client.key("Room", id)
                enitity_exists = datastore_client.get(key=entity_key)
                if enitity_exists:
                    query_2 = datastore_client.query(kind="BookingRoomList")
                    query_2 = query_2.add_filter('rmname', '=', id).fetch()
                    for i in query_2:
                        name_list.append(dict(i))

                if(len(name_list)==0):
                    entity_key = datastore_client.key("Room", id)
                    datastore_client.delete(key=entity_key)
                    name_list = getAvailableRoomData();
                    return render_template("available_roomlist.html", user_data=user_data, rooms=name_list)
                else:
                    error_message = "This room is alreday booked by a user.Hence it can't be delete"
                    return render_template("error.html", error_message=error_message)

            else:
                error_message = "Page not loaded! User Data is missing"
                return render_template("error.html", error_message=error_message)
        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("error.html", error_message=error_message)
@app.route("/editRoomBookSearchResult", methods=["GET", "POST"])
def editRoomBookSearchResult():
    user_data =checkUserData();
    if user_data != None:
        try:
            data = dict(request.form)
            startDate = data.get("fromDate")
            endDate = data.get("toDate")
            rmType  = data.get("roomType")
            rmbookingId = data.get("bookedRmData")
            bookingData = data.get("booking")
            bookingData = bookingData.replace("'", "\"")
            bookingData=json.loads(bookingData)

            todayDate = datetime.today()
            fromDate=datetime.fromisoformat(startDate)
            ToDate =datetime.fromisoformat(endDate)

            oldFromDate =bookingData["startdate"]
            oldToDate =bookingData["enddate"]
            oldFromDate=datetime.fromisoformat(oldFromDate)
            oldToDate=datetime.fromisoformat(oldToDate)
            oldType =bookingData["type"]
            userDetails = getUserDetails(rmbookingId)
            if(fromDate==oldFromDate and ToDate==oldToDate and rmType==oldType):
                return render_template("edit_booking.html" ,user_data=user_data,bookedRmData = bookingData, userDetails=userDetails)
            else:
                """
                if((oldFromDate != fromDate) or (oldToDate!= ToDate) or(rmType!=oldType) ):
                    bookingKey = bookingData['rmname']+"|"+str(fromDate)+"|"+str(ToDate)+"|"+user_data['email']
                    entity_key = datastore_client.key("BookingRoomList", bookingKey)
                    enitity_exists = datastore_client.get(key=entity_key)
                    if enitity_exists:
                        return_url = '/bookedroomlist/AllType'
                        error_message = "an entry with same name already exists. try with an another name"
                        return render_template("error.html", error_message=error_message,return_url=return_url)
                    else:
                        entity_key_old = datastore_client.key("BookingRoomList", bookingKey)
                        datastore_client.delete(key=entity_key_old)"""
                if(ToDate < fromDate):
                    return_url = '/bookedroomlist/AllType'
                    error_message = "Check-in date should be less than Check-out Date"
                    return render_template("error.html", error_message=error_message,return_url=return_url)
                if(todayDate >= fromDate):
                    return_url = '/bookedroomlist/AllType'
                    error_message = "User can't select previous dates as checkin date"
                    return render_template("error.html", error_message=error_message,return_url=return_url)
                booking={}
                booking["fromDate"] = startDate
                booking["toDate"] = endDate
                booking["rmType"] = rmType
                booking["rmName"] = bookingData['rmname']
                name_list = getBookingRoomFilter(booking)

                if name_list:
                    booking["rmPrice"] =name_list[0]["price"]
                    booking["req"] =name_list[0]["req"]
                    name_list[0]["fromDate"] = startDate
                    name_list[0]["toDate"] = endDate
                    name_list[0]["startdate"] = name_list[0]["fromDate"]
                    name_list[0]["enddate"] = name_list[0]["toDate"]
                    name_list[0]["rmname"] = name_list[0]["name"]

                    name_list[0]["bookingKey"] = "nobookingid"
                    return render_template("edit_booking.html" ,user_data=user_data,bookedRmData = name_list[0],bookingOldData=rmbookingId,userDetails=userDetails)
                else:
                    return_url = '/bookedroomlist/AllType'
                    error_message = "An entry with same date is already exists. try with an another date/time, \n OR \n No room available for '"+rmType+"' room type"
                    return render_template("error.html", error_message=error_message,return_url=return_url)

        except ValueError as exc:
            error_message = str(exc)
            return render_template("error.html", error_message=error_message)
    else:
        error_message = "Page not loaded! User Data is missing"
        return render_template("index.html", user_data=user_data, error_message=error_message)


@app.route("/singnout", methods=["GET", "POST"])
def signOut():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
