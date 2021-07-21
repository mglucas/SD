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
import pickle
import serpent
from ast import literal_eval
from rich import print
from rich.console import Console
import Pyro4
import Pyro4.naming
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
""" ------------------------ """

HOSTNAME = "127.0.0.1"
SERVER_NAME = "rt.server"

# -------------------------------- CLASSES --------------------------------

@Pyro4.behavior(instance_mode="single")
class Server(object):
    """
    Description: this class implements the server functionalities. It includes
                 serving user calls, maintaining their data and notifying
                 them when necessary.
    
    Attributes:
    - clients (list): list containing all clients as dictionaries;
    - rides (list): list containing all rides (from drivers) as dictionaries;
    - requests (list): list containing all requests (from passengers) as
                       dictionaries;
    - current_id (int): unique integer ID constantly update to create new
                        subscriptinos.
        
    Methods:
    - addClient: register new client in server;
    - getClient: get client from list of clients given their unique name;
    - addSubscription: add new client subscription;
    - delSubscription: delete a client subscription by ID;
    - checkNotify: check if any other subscriptins match a new addition and
                   notify the adequate correspondent clients if necessary;
    - getAvailableRides: returns available rides (from drivers);
    - getAvailableRequests: returns available requests (from passengers);
    - getClientSubscriptions: return subscriptions (both rides and requests)
                              for a given client.
    """

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


    @Pyro4.expose
    def addClient(self, name, contact, public_key):
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


    @Pyro4.expose
    def getClient(self, name):
        """
        Description: get client by name.
        
        Parameters:
        - name (string): client name (unique key).

        Returns:
        - (Client): correpondent client.
        """
        client = next((client for client in self.clients if client["name"] == name), None)
        if client == None:
            print(f"\nCould not find client {name}!!!\n")

        return client


    @Pyro4.expose
    def addSubscription(self, message, signature):
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
        self.clients = pickleload("clients")
        self.rides = pickleload("rides")
        self.requests = pickleload("requests")
        self.current_id = pickleload("current_id")

        # Why use serpent: https://pyro4.readthedocs.io/en/stable/tipstricks.html#binary-data-transfer-file-transfer
        message = serpent.tobytes(message)
        message_dict = message.decode('utf-8')
        message_dict = literal_eval(''.join(message_dict))

        client = self.getClient(message_dict["name"])

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


    @Pyro4.expose
    def delSubscription(self, id):
        """
        Description: deletes already existing subscription.
        
        Parameters:
        - id (int): unique ID of the subscription to be deleted.

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
    
    @Pyro4.expose
    def getAvailableRides(self, origin, destination, date):
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
        self.rides = pickleload("rides")
        return [ride for ride in self.rides
                    if (ride["origin"] == origin 
                    and ride["destination"] == destination 
                    and ride["date"] == date)]


    def getAvailableRequests(self, origin, destination, date):
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
        self.requests = pickleload("requests")
        return [request for request in self.requests
                    if (request["origin"] == origin 
                    and request["destination"] == destination
                    and request["date"] == date)]


    @Pyro4.expose
    def getClientSubscriptions(self, name):
        """
        Description: return subscriptions for a given client.
        
        Parameters:
        - name (string): name (unique key) of the client.

        Returns:
        - (tuple): a tuple contaning two lists: the first with the requests
                   and the second with the rides of the given user. 
        """
        self.rides = pickleload("rides")
        self.requests = pickleload("requests")
        return ([request for request in self.requests if request["name"] == name],
                [ride for ride in self.rides if ride["name"] == name])

# --------------------------------------------------------------------------


# -------------------------------- FUNCTIONS -------------------------------

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


def startNSThread():
    """
    Description: function responsible for initiating the name server as a thread.
    
    Parameters:
    - None

    Returns:
    - None
    """
    try: 
        print("[bold yellow]NameServer[/bold yellow]: Starting ")
        thread = Thread(target=Pyro4.naming.startNSloop,args=(HOSTNAME,))
        thread.daemon = True
        thread.start()
        time.sleep(1)
        print("[bold yellow]NameServer[/bold yellow]: Running!\n")
    except: 
        print("[bold yellow]NameServer[/bold yellow]: [red]Error![/red] Check NameServer \n")
        exit


def cleanUpFiles():
    """
    Description: function responsible for deleting the pickles at the end of
                 the execution of the server (thus not keeping the data on
                 following executions).
    
    Parameters:
    - None

    Returns:
    - None
    """
    if Path("clients.pickle").is_file():
        os.remove("clients.pickle")
    if Path("current_id.pickle").is_file():
        os.remove("current_id.pickle")
    if Path("requests.pickle").is_file():
        os.remove("requests.pickle")
    if Path("rides.pickle").is_file():
        os.remove("rides.pickle")

# --------------------------------------------------------------------------


# ---------------------------------- MAIN ----------------------------------

def main():
    
    startNSThread()

    print("[bold chartreuse3]Server[/bold chartreuse3]: Registering on Name Server... ")
    print("[bold chartreuse3]Server[/bold chartreuse3]: Wait for \"Pyro daemon running\". ")

    # Registering Pyro class as a daemon in name server
    Pyro4.Daemon.serveSimple(
        {
            Server: SERVER_NAME
        },
        ns = True)

    print("[bold chartreuse3]Server[/bold chartreuse3]: Killing the server :(")

    cleanUpFiles()

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit()

# --------------------------------------------------------------------------