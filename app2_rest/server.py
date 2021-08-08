# -*- coding: utf-8 -*-
""" ===========================================================================
Created on July 8 2021

@authors: Lucas Ricardo Marques de Souza
          Victor Feitosa Lourenco

This python script was created for the Distribuited Systems course for the
Computer Engineering major at the Federal University of Technology - Parana.
=========================================================================== """

""" --------- IMPORTS --------- """
# Libraries
import os
import time
import sys
import json
from pathlib import Path
from threading import Thread
from types import MethodDescriptorType
from rich import print
from rich.console import Console
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler

""" ------------------------ """

HOSTNAME = "127.0.0.1"
SERVER_NAME = "rt.server"


app = Flask(__name__)
CORS(app)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


# API index page
@app.route('/')
def index():
    # abort(404)
    return "Welcome to RideTogether!"


# -------------------------------- CLASSES --------------------------------


print ("[bold chartreuse3]Server[/bold chartreuse3]: Initilized a server instance")
global clients
global rides
global requests
# Current ID is different for rides and requests to facilitate filtering
# (requests are odd, rides are even)
global current_id

clients = []
rides = []
requests = []
current_id = 100

clients.append({
    "name" : "name",      # unique key for each client
    "contact" : "contact"
})

@app.route('/clients', methods=['POST'])
def addClient():
    """
    Description: add new client with required atributes.
    
    Parameters:
    - name (string): client name (used as primary key for each client);
    - contact (string): client email.

    Returns:
    - (bool): 'True' for when the client was added successfully and 'False'
                otherwise.
    """
    global clients
    
    content = request.json['data']

    name = content["name"]
    contact = content["contact"]

    # Check if client already exists
    if (name in [d["name"] for d in clients]):
        return jsonify(success=False)

    clients.append({
        "name" : name,      # unique key for each client
        "contact" : contact
    })

    console = Console()
    print("\n[bold chartreuse3]Server[/bold chartreuse3]: ", end="")
    console.print(name, style="bold orange3", end="")
    print(" registered successfully.")

    return jsonify(success=True)

@app.route('/clients/<name>', methods=['GET'])
def getClient(name):
    """
    Description: get client by name.
    
    Parameters:
    - name (string): client name (unique key).

    Returns:
    - (Client): correpondent client.
    """
    global clients

    client = next((client for client in clients if client["name"] == name), None)
    if client == None:
        print(f"\nCould not find client {name}!!!\n")
        return jsonify(success=False)

    return jsonify(success=True)

@app.route('/clients', methods=['GET'])
def getAllClients():
    global clients
    return jsonify(clients)

@app.route('/subscriptions', methods=['POST'])
def addSubscription():
    """
    Description: add new subscription (ride or request) to a client.
                    The communication between the client and the server is
                    done with a signature, which the server verifies to confirm
                    the client's identity.
    
    Parameters:
    - message (string): encoded mesage from client. This contains a dictionary
                        with 5 or 6 items depending on whether it's a ride or
                        request:
                        - name: name of the client (subscriber),
                        - reference: remote object reference of the client, 
                        - origin: selected origin of the drive,
                        - destination: selected destination of the drive,
                        - date:  selected date of the drive,
                        - passengers (only for ride): max number of passengers;
    - signature (bytes): signature of the message.
    

    Returns:
    - self.current_id (int): unique attributed ID of the subscription.
    """
    #global clients
    global rides, requests, current_id

    message = request.json["message"]
    client = getClient(message["name"])

    # Identifies if the message relates to a request or ride
    if len(message) == 5:
        current_id += 1
        if not(current_id % 2):
            current_id += 1
        requests.append({
            "id"          : current_id,
            "name"        : message["name"],
            "origin"      : message["origin"],
            "destination" : message["destination"],
            "date"        : message["date"]
        })
    else:
        current_id += 1
        if current_id % 2:
            current_id += 1
        rides.append({
            "id"          : current_id,
            "name"        : message["name"],
            "origin"      : message["origin"],
            "destination" : message["destination"],
            "date"        : message["date"],
            "passengers"  : message["passengers"]
        })

    checkNotify(client, message)

    return {"id" : current_id}


@app.route('/subscriptions/<id>', methods=['DELETE'])
def delSubscription(id):
    """
    Description: deletes already existing subscription.
    
    Parameters:
    - id (int): unique ID of the subscription to be deleted.

    Returns:
    - None
    """
    try:
        if id % 2:
            del_sub = next(req for req in requests if req["id"] == id )
            requests.remove(del_sub)
        else:
            del_sub = next(ride for ride in rides if ride["id"] == id )
            rides.remove(del_sub)
    except:
        return jsonify(success=False)

    return jsonify(success=True)


def checkNotify(new_client, new_sub):
    """
    Description: method called everytime a new subscription is added to check
                    if any other subscription matches the new one (an already
                    existing ride for a new request or an already existing
                    request for a new ride). Notifies correpondent client if
                    necessary (via the remote object reference).
    
    Parameters:
    - new_client (dict): item from self.clients list cointaining name, contact,
                            public key and reference;
    - new_sub (dict): new subscriber, received as message from client, containing
                        the items described in message (string) of the
                        addSubscription method.

    Returns:
    - None
    """
    if len(new_sub) == 5:
        matches = availableRides(new_sub["origin"], new_sub["destination"], new_sub["date"])
    else:
        matches = availableRequests(new_sub["origin"], new_sub["destination"], new_sub["date"])

    if matches != []:
        for match in matches:
            client = getClient(match["name"])

            sse.publish({"id": match["id"], "name": new_client["name"], "contact" : new_client["contact"]},
                        type='publish',
                        channel=client["name"])


def availableRides(origin, destination, date):
    """
    Description: return available rides given certain constraints.
    
    Parameters:
    - origin (string): selected origin of the drive,
    - destination (string): selected destination of the drive,
    - date (string): selected date of the drive.

    Returns:
    - (list): list of items from self.rides list cointaining subscription ID,
                client name, drive origin, destination and date and number of passengers.
    """
    global rides

    return [ride for ride in rides
                if (ride["origin"] == origin 
                and ride["destination"] == destination 
                and ride["date"] == date)]


def availableRequests(origin, destination, date):
    """
    Description: return available requests given certain constraints.
    
    Parameters:
    - origin (string): selected origin of the drive,
    - destination (string): selected destination of the drive,
    - date (string): selected date of the drive.

    Returns:
    - (list): list of items from self.requests list cointaining subscription ID,
                client name, drive origin, destination and date.
    """
    global requests

    return [request for request in requests
                if (request["origin"] == origin 
                and request["destination"] == destination
                and request["date"] == date)]


@app.route('/subscriptions/rides', methods=['GET'])
def getAvailableRides():
    """

    """
    origin = request.args.get("origin", type = str)
    destination = request.args.get("destination", type = str)
    date = request.args.get("date", type = str)

    return  {"ride": getAvailableRides(origin, destination, date)}


@app.route('/subscriptions/<name>', methods=['GET'])
def getClientSubscriptions(name):
    """
    Description: return subscriptions for a given client.
    
    Parameters:
    - name (string): name (unique key) of the client.

    Returns:
    - (tuple): a tuple contaning two lists: the first with the requests
                and the second with the rides of the given user. 
    """
    global rides, requests

    return {"requests": [request for request in requests if request["name"] == name],
            "rides": [ride for ride in rides if ride["name"] == name]}



# --------------------------------------------------------------------------


# -------------------------------- FUNCTIONS -------------------------------
# --------------------------------------------------------------------------


# ---------------------------------- MAIN ----------------------------------

def main():
    app.run(debug=True)

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit()

# --------------------------------------------------------------------------