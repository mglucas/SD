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
import random
from ast import literal_eval
from rich import print
from rich.console import Console
import Pyro4
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
""" ------------------------ """

# -TODO- document stuff

# Start name server
## python -m Pyro4.naming
# Check NS list 
## python -m Pyro4.nsc list

@Pyro4.expose
class Server(object):
    def __init__(self):
        print ("server ok")
        self.clients = []
        self.rides = []
        self.requests = []
        # Current ID is different for rides and requests to facilitate filtering
        # (requests are odd, rides are even)
        self.current_id = 100
    

    def addClient(self, name, contact, public_key):
        self.clients.append({
            "name" : name,
            "contact" : contact,
            "publickey" : public_key
        })
        console = Console()
        print("\n[bold chartreuse3]Server[/bold chartreuse3]: ", end="")
        console.print(name, style="bold orange3", end="")
        print(" registered successfully.")


    def addSubscription(self, message, signature):
        decoded_message = literal_eval(message.decode("utf-8"))
        # -TODO- CHECK KEY (REFERENCE or NAME)
        client = next(client for client in self.clients if client["name"] == decoded_message["name"])

        try:
            client["publickey"].verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            print("\n[bold chartreuse3]Server[/bold chartreuse3]: Valid signature at the server!")
        except InvalidSignature:
            print("\n[bold chartreuse3]Server[/bold chartreuse3]: Invalid signature")

        # Identifies if the message relates to a request or ride
        if len(decoded_message) == 5:
            self.current_id += 1
            if not(self.current_id % 2):
                self.current_id += 1
            self.requests.append({
                "id"          : self.current_id,
                "reference"   : decoded_message["reference"],
                "name"        : decoded_message["name"],
                "origin"      : decoded_message["origin"],
                "destination" : decoded_message["destination"],
                "date"        : decoded_message["date"]
            })
        else:
            self.current_id += 1
            if self.current_id % 2:
                self.current_id += 1
            self.rides.append({
                "id"          : self.current_id,
                "reference"   : decoded_message["reference"],
                "name"        : decoded_message["name"],
                "origin"      : decoded_message["origin"],
                "destination" : decoded_message["destination"],
                "date"        : decoded_message["date"],
                "passengers"  : decoded_message["passengers"]
            })

        return self.current_id

    def delSubscription(self, id):
        if id % 2:
            del_request = next(req for req in self.requests if req["id"] == id )
            self.requests.remove(del_request)
        else:
            del_ride = next(ride for ride in self.rides if ride["id"] == id )
            self.rides.remove(del_ride)

    def getAvailableRides(self,origin,destination,date):
        return [ride for ride in self.rides if (ride["origin"] == origin 
                                            and ride["destination"] == destination 
                                            and ride["date"] == date)]
    
    def getClientSubscriptions(self, reference):
        # -TODO- CHECK KEY (REFERENCE or NAME)
        return ([request for request in self.requests if request["reference"] == reference],
                [ride for ride in self.rides if ride["reference"] == reference])

def main():
    print("Server main function")
    # Registering Pyro class as a daemon in name server
    Pyro4.Daemon.serveSimple(
            {
                Server: "rt.server"
            },
            ns = True)

if __name__=="__main__":
    main()