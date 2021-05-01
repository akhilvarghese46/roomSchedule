from flask import Flask, render_template, request, redirect
from google.auth.transport import requests
import google.oauth2.id_token
from datetime import datetime
import random
from google.cloud import datastore

from models import Room

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
    query = datastore_client.query(kind="Room").fetch()
    for i in query:
        name_list.append(dict(i))
    return name_list

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

@app.route("/singnout", methods=["GET", "POST"])
def signOut():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
