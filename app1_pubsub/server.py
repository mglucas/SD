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
from pathlib import Path
import pickle
import serpent
from ast import literal_eval
from rich import print
from rich.console import Console
import Pyro4
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
""" ------------------------ """

""" 
    TODO-Victor document stuff
    TODO-Mega @Pyro4.expose on necessary methods. Exclude private methods.
    TODO-Mega Start nameserver from code 
"""
# Start name server
## python -m Pyro4.naming
# Check NS list 
## python -m Pyro4.nsc list

@Pyro4.expose
class Server(object):
    def __init__(self):
        print ("[bold chartreuse3]Server[/bold chartreuse3]: Initilized a server instance")
        
        self.clients = pickleload("clients") if Path("clients.pickle").is_file() else []
        self.rides = pickleload("rides") if Path("rides.pickle").is_file() else []
        self.requests = pickleload("requests") if Path("requests.pickle").is_file() else []
        # Current ID is different for rides and requests to facilitate filtering
        # (requests are odd, rides are even)
        self.current_id = pickleload("current_id") if Path("current_id.pickle").is_file() else 100

        pickledump(self.clients, 'clients')
        pickledump(self.rides, 'rides')
        pickledump(self.requests, 'requests')
        pickledump(self.current_id, 'current_id')


    def addClient(self, name, contact, public_key):
        """
        Description: .
        
        Parameters:
        - x (string): .

        Returns:
        - None
        """
        print("[bold chartreuse3]Server[/bold chartreuse3]: Adding client")
        self.clients = pickleload("clients")

        # Check if client already exists
        if (name in [d["name"] for d in self.clients]):
            return False

        self.clients.append({
            "name" : name,      # unique key for each client
            "contact" : contact,
            "publickey" : public_key,
            "reference": None
        })
        pickledump(self.clients, 'clients')

        console = Console()
        print("\n[bold chartreuse3]Server[/bold chartreuse3]: ", end="")
        console.print(name, style="bold orange3", end="")
        print(" registered successfully.")

        return True


    def addSubscription(self, message, signature):
        """
        Description: .
        
        Parameters:
        - x (string): .

        Returns:
        - None
        """
        self.clients = pickleload("clients")
        self.rides = pickleload("rides")
        self.requests = pickleload("requests")
        self.current_id = pickleload("current_id")

        # Why use serpent: https://pyro4.readthedocs.io/en/stable/tipstricks.html#binary-data-transfer-file-transfer
        message = serpent.tobytes(message)
        message_dict = message.decode('utf-8')
        message_dict = literal_eval(''.join(message_dict))

        client = next((client for client in self.clients if client["name"] == message_dict["name"]), None)
        if client == None:
            print(f"Could not find client {message_dict['name']}!!!")

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
            print("\n[bold chartreuse3]Server[/bold chartreuse3]: Valid signature at the server!")
        except InvalidSignature:
            print("\n[bold chartreuse3]Server[/bold chartreuse3]: Invalid signature")

        if client["reference"] == None:
            client["reference"] = message_dict["reference"]

        # Identifies if the message relates to a request or ride
        if len(message_dict) == 5:
            self.current_id += 1
            if not(self.current_id % 2):
                self.current_id += 1
            self.requests.append({
                "id"          : self.current_id,
                "name"        : message_dict["name"],
                "origin"      : message_dict["origin"],
                "destination" : message_dict["destination"],
                "date"        : message_dict["date"]
            })
        else:
            self.current_id += 1
            if self.current_id % 2:
                self.current_id += 1
            self.rides.append({
                "id"          : self.current_id,
                "name"        : message_dict["name"],
                "origin"      : message_dict["origin"],
                "destination" : message_dict["destination"],
                "date"        : message_dict["date"],
                "passengers"  : message_dict["passengers"]
            })

        self.checkNotify(client, message_dict)

        pickledump(self.clients, "clients")
        pickledump(self.rides, "rides")
        pickledump(self.requests, "requests")
        pickledump(self.current_id, "current_id")

        return self.current_id


    def delSubscription(self, id):
        """
        Description: .
        
        Parameters:
        - x (string): .

        Returns:
        - None
        """
        if id % 2:
            self.requests = pickleload("requests")
            del_request = next(req for req in self.requests if req["id"] == id )
            self.requests.remove(del_request)
            pickledump(self.requests, "requests")
        else:
            self.rides = pickleload("rides")
            del_ride = next(ride for ride in self.rides if ride["id"] == id )
            self.rides.remove(del_ride)
            pickledump(self.rides, "rides")


    def checkNotify(self, new_client, new_sub):
        """
        Description: .
        
        Parameters:
        - x (string): .

        Returns:
        - None
        """
        if len(new_sub) == 5:
            matches = [ride for ride in self.rides if ride["origin"] == new_sub["origin"]
                                                  and ride["destination"] == new_sub["destination"]
                                                  and ride["date"] == new_sub["date"]]
            if matches != []:
                for match in matches:
                    client = next(client for client in self.clients if client["name"] == match["name"])

                    client_p = Pyro4.Proxy(client["reference"])
                    client_p.notifyAvailablePassenger(new_client["name"], new_client["contact"])
        else:
            matches = [request for request in self.requests if request["origin"] == new_sub["origin"]
                                                           and request["destination"] == new_sub["destination"]
                                                           and request["date"] == new_sub["date"]]
            if matches != []:
                for match in matches:
                    client = next(client for client in self.clients if client["name"] == match["name"])

                    client_p = Pyro4.Proxy(client["reference"])
                    client_p.notifyAvailableDriver(new_client["name"], new_client["contact"])
    
    
    def getAvailableRides(self,origin,destination,date):
        """
        Description: .
        
        Parameters:
        - x (string): .

        Returns:
        - None
        """
        self.rides = pickleload("rides")
        return [ride for ride in self.rides if (ride["origin"] == origin 
                                            and ride["destination"] == destination 
                                            and ride["date"] == date)]
    

    def getClientSubscriptions(self, name):
        """
        Description: .
        
        Parameters:
        - name (string): .

        Returns:
        - None
        """
        self.rides = pickleload("rides")
        self.requests = pickleload("requests")
        return ([request for request in self.requests if request["name"] == name],
                [ride for ride in self.rides if ride["name"] == name])


def pickledump(dumped_data, name):
    """
    Description: simple formalization of the function "dump" from the library
                 pickle. Open new file with given name and dump given data.
    
    Parameters:
    - dumped_data (undefined): data to be dumped, which could be of any type;
    - name (string): name with which the file will be saved.

    Returns:
    - None
    """
    with open(f'{name}.pickle', 'wb') as handle:
        pickle.dump(dumped_data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def pickleload(name):
    """
    Description: simple formalization of the function "load" from the library
                 pickle. Open file that has the given name and load its data.
    
    Parameters:
    - name (string): string name of the file that will be opened and loaded;
    - direct_path (string): path for the exact location where the pickle should
                            be loaded from.

    Returns:
    - loaded_data (undefined): data retreived from pickle file.
    """

    with open(f"{name}.pickle", 'rb') as handle:
        loaded_data = pickle.load(handle)
    if loaded_data == None:
        return []
    return loaded_data


def main():
    print("Server main function")
    # Registering Pyro class as a daemon in name server
    Pyro4.Daemon.serveSimple(
        {
            Server: "rt.server"
        },
        ns = True)

    print("[bold chartreuse3]Server[/bold chartreuse3]: Killing the server :(")
    if Path("clients.pickle").is_file():
        os.remove("clients.pickle")
    if Path("current_id.pickle").is_file():
        os.remove("current_id.pickle")
    if Path("requests.pickle").is_file():
        os.remove("requests.pickle")
    if Path("rides.pickle").is_file():
        os.remove("rides.pickle")


if __name__=="__main__":
    main()