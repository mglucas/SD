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
from pathlib import Path
from threading import Thread
import serpent
from ast import literal_eval
from rich import print
from rich.console import Console
from flask import Flask, abort, render_template
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler

""" ------------------------ """

HOSTNAME = "127.0.0.1"
SERVER_NAME = "rt.server"


app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')


# API index page
@app.route('/')
def index():
    # abort(404)
    return {'name': 'Welcome to RideTogether!', 'num_pas': 4}


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


def addClient(name, contact, public_key):
    """
    Description: add new client with required atributes.
    
    Parameters:
    - name (string): client name (used as primary key for each client);
    - contact (string): client email;
    - public_key (bytes): serialized public key.

    Returns:
    - (bool): 'True' for when the client was added successfully and 'False'
                otherwise.
    """
    print("[bold chartreuse3]Server[/bold chartreuse3]: Adding client")

    # Check if client already exists
    if (name in [d["name"] for d in clients]):
        return False

    clients.append({
        "name" : name,      # unique key for each client
        "contact" : contact,
        "publickey" : public_key,
        "reference": None
    })

    console = Console()
    print("\n[bold chartreuse3]Server[/bold chartreuse3]: ", end="")
    console.print(name, style="bold orange3", end="")
    print(" registered successfully.")

    return True


# API index page
@app.route('/getclients')
def getClient(name):
    """
    Description: get client by name.
    
    Parameters:
    - name (string): client name (unique key).

    Returns:
    - (Client): correpondent client.
    """
    client = next((client for client in clients if client["name"] == name), None)
    if client == None:
        print(f"\nCould not find client {name}!!!\n")

    return client
    # global current_id


    # current_id += 1
    # if(current_id % 2):
    #     sse.publish({"Canal": "1", "status": "Active", "number": current_id }, type='publish', channel="channel1")

    # sse.publish({"Canal": "2", "status": "Active", "number": current_id }, type='publish', channel=str(current_id))


    # return f"PAR ativa o canal 1 \n - IMPAR ativa o canal 2 \n number -> {current_id}"


def addSubscription(message, signature):
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
    # Why use serpent: https://pyro4.readthedocs.io/en/stable/tipstricks.html#binary-data-transfer-file-transfer
    message = serpent.tobytes(message)
    message_dict = message.decode('utf-8')
    message_dict = literal_eval(''.join(message_dict))

    client = getClient(message_dict["name"])

    client_public_key  = serialization.load_pem_public_key(
        serpent.tobytes(client["publickey"]),
        backend=default_backend()        
    )

    signature = serpent.tobytes(signature)
    try:
        client_public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("\n[bold chartreuse3]Server[/bold chartreuse3]: "
                "Valid signature at the server!")
    except InvalidSignature:
        print("\n[bold chartreuse3]Server[/bold chartreuse3]: "
                "[bold red]Invalid signature[/bold red]")

    if client["reference"] == None:
        client["reference"] = message_dict["reference"]

    # Identifies if the message relates to a request or ride
    if len(message_dict) == 5:
        current_id += 1
        if not(current_id % 2):
            current_id += 1
        requests.append({
            "id"          : current_id,
            "name"        : message_dict["name"],
            "origin"      : message_dict["origin"],
            "destination" : message_dict["destination"],
            "date"        : message_dict["date"]
        })
    else:
        current_id += 1
        if current_id % 2:
            current_id += 1
        rides.append({
            "id"          : current_id,
            "name"        : message_dict["name"],
            "origin"      : message_dict["origin"],
            "destination" : message_dict["destination"],
            "date"        : message_dict["date"],
            "passengers"  : message_dict["passengers"]
        })

    checkNotify(client, message_dict)

    return current_id


def delSubscription(id):
    """
    Description: deletes already existing subscription.
    
    Parameters:
    - id (int): unique ID of the subscription to be deleted.

    Returns:
    - None
    """
    if id % 2:
        del_request = next(req for req in requests if req["id"] == id )
        requests.remove(del_request)
    else:
        del_ride = next(ride for ride in rides if ride["id"] == id )
        rides.remove(del_ride)


def checkNotify(self, new_client, new_sub):
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
        matches = self.getAvailableRides(new_sub["origin"], new_sub["destination"], new_sub["date"])
        
        if matches != []:
            for match in matches:
                client = self.getClient(match["name"])

                client_p = Pyro4.Proxy(client["reference"])
                client_p.notifyAvailablePassenger(new_client["name"], new_client["contact"])
    else:
        matches = self.getAvailableRequests(new_sub["origin"], new_sub["destination"], new_sub["date"])

        if matches != []:
            for match in matches:
                client = self.getClient(match["name"])

                client_p = Pyro4.Proxy(client["reference"])
                client_p.notifyAvailableDriver(new_client["name"], new_client["contact"])

def getAvailableRides(origin, destination, date):
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
    return [ride for ride in rides
                if (ride["origin"] == origin 
                and ride["destination"] == destination 
                and ride["date"] == date)]


def getAvailableRequests(origin, destination, date):
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
    return [request for request in requests
                if (request["origin"] == origin 
                and request["destination"] == destination
                and request["date"] == date)]


def getClientSubscriptions(name):
    """
    Description: return subscriptions for a given client.
    
    Parameters:
    - name (string): name (unique key) of the client.

    Returns:
    - (tuple): a tuple contaning two lists: the first with the requests
                and the second with the rides of the given user. 
    """
    return ([request for request in requests if request["name"] == name],
            [ride for ride in rides if ride["name"] == name])



# --------------------------------------------------------------------------


# -------------------------------- FUNCTIONS -------------------------------
# --------------------------------------------------------------------------


# ---------------------------------- MAIN ----------------------------------

def main():
    app.run()

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit()

# --------------------------------------------------------------------------