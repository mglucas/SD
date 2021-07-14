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
import sys
import time
from threading import Thread
import stdiomask
from rich import print
from rich.console import Console
from prettytable import PrettyTable
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import Pyro4
import Pyro4.util

# Internal Modules
# from server import Server
""" ------------------------ """


class Client(object):
    """
    Description: this class implements the client user functionalities.
                 It includes management of it's attributes, exchanges with
                 the server and terminal user interface interaction.
    
    Attributes:
    - name (str): name of the client only set on creation;
    - contact (str): contact of the client (email) only set on creation;
    - password (str): client password.
    - subscriptions
    - priv_key -TODO- FINISH THIS
    - pub_key 
    - reference  
        
    Methods:
    - registerInServer: ;
    - displaySubscriptions: .
    """

    def __init__(self, name, contact, password):
        self.name = name
        self.contact = contact
        self.password = password
        self.subscriptions = []
        
        # Private and public keys
        self.priv_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.pem_priv_key = self.priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        self.pub_key = self.priv_key.public_key()
        self.pem_pub_key = self.pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        daemon = Pyro4.core.Daemon()
        self.reference = str(daemon.register(self))
        thread = Thread(target=daemon.requestLoop)
        thread.daemon = True
        thread.start()


    def registerInServer(self, server):
        """
        Description: calls server method to register new client; this is done
                     on creation of the object.
        
        Parameters:
        - server (Server): Server instance which is hosting the application.

        Returns:
        - None
        """
        print(f"This is {self.name} registering in server.")
        
        # Checks if client is not already registered
        if(server.addClient(self.name, self.contact, self.pem_pub_key)):
            print("Success!")
        else: 
            print("Fail! User already exists")

    @staticmethod
    def displaySubscriptions(subs):
        """
        Description: auxiliary function which organizedly displays a client's
                     subscriptions (rides and requests).
        
        Parameters:
        - subs (tuple): contains two lists of subscriptions, the first
                        with the client's requests and the seconds with
                        their rides.

        Returns:
        - None
        """
        requests_table = PrettyTable()
        rides_table = PrettyTable()

        print(" - Want to be a passenger:")
        if subs[0] == []:
            print("\tNot subscribed to any rides yet!")
        else:
            requests_table.field_names = ["ID", "Origin", "Destination", "Date"]
            for request in subs[0]:
                requests_table.add_row([request["id"], request["origin"],
                                        request["destination"], request["date"]])
            print(requests_table)
        
        print("\n - Want to be a driver:")
        if subs[1] == []:
            print("\tNot subscribed to any rides yet!")
        else:
            rides_table.field_names = ["ID", "Origin", "Destination", "Date", "Passengers"]
            for ride in subs[1]:
                rides_table.add_row([ride["id"], ride["origin"], ride["destination"],
                                     ride["date"], ride["passengers"]])
            print(rides_table)


    def delSubscription(self, server):
        """
        Description: .
        
        Parameters:
        - server (Server): Server instance which is hosting the application.

        Returns:
        - None
        """
        print(" ------ [bold] Deleting Subscription [/bold] ------")
        
        subs = server.getClientSubscriptions(self.name)
        self.displaySubscriptions(subs)

        print("Choose an ID to unsubscribe from or return to the user menu.\n"
              " 0 - Return to user menu")
        id = int(input())

        while(id not in self.subscriptions):
            print("[bold underline]Invalid option![/bold underline]")
            id = int(input())

        if id in self.subscriptions:
            self.subscriptions.remove(id)
            print(self.subscriptions)

            server.delSubscription(id)


    def addSubscription(self, server):
        """
        Description: call host server to add a subscription to this Client. This
                     method also communicates with the user regarding the details
                     of the subscription (which can be a ride or a request).
        
        Parameters:
        - server (Server): Server instance which is hosting the application.

        Returns:
        - None
        """
        print(" ------ [bold] Adding Subscription [/bold] ------")
        print("Do you want to be a driver or a passenger?\n"
              " 1 - Driver \n 2 - Passenger \n 3 - Return to user menu")
        value = int(input())
        while(value not in [1, 2, 3]):
            print("[bold underline]Invalid option![/bold underline]")
            value = int(input())
        os.system('cls')

        if value == 3:
            return

        print(" ------ [bold] Adding Subscription [/bold] ------")
        
        message = {"name":self.name, "reference":self.reference}

        if value == 1:
            print("OK! We need to know a few things about the ride you want to give.\n"
                  " [bold bright_cyan]Origin location[/bold bright_cyan]: ", end="")
            message["origin"] = str(input())
            print(" [bold bright_cyan]Destination location[/bold bright_cyan]: ", end="")
            message["destination"] = str(input())
            print(" [bold bright_cyan]Date of the ride[/bold bright_cyan]: ", end="")
            message["date"] = str(input())
            print(" [bold bright_cyan]Max number of passengers[/bold bright_cyan]: ", end="")
            message["passengers"] = str(input())
        
        elif value == 2:
            print("OK! We need to know a few things about the ride you want to take.\n"
                  " [bold bright_cyan]Origin location[/bold bright_cyan]: ", end="")
            message["origin"] = str(input())
            print(" [bold bright_cyan]Destination location[/bold bright_cyan]: ", end="")
            message["destination"] = str(input())
            print(" [bold bright_cyan]Date of the ride[/bold bright_cyan]: ", end="")
            message["date"] = str(input())

        # Turns dictionary message to string and encodes it to bytes
        message = str(message).encode('utf_8')
        signature = self.priv_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        self.subscriptions.append(server.addSubscription(message, signature))
        print("New subscription successfully added! Returning to user menu...")
        time.sleep(3)
        

    def interact(self, server):
        """
        Description: represents the client menu, where the user will interact
                     with the host server manage their subscriptions.
        
        Parameters:
        - server (Server): Server instance which is hosting the application.

        Returns:
        - None
        """
        while True:
            print(" ------ [bold] User Menu [/bold] ------")
            console = Console()
            print("Hello ", end="")
            console.print(self.name, style="bold orange3", end="")
            print("!\nThese are your active subscriptions:\n")
            
            subs = server.getClientSubscriptions(self.name)
            self.displaySubscriptions(subs)

            print("\nWhat do you wish to do?\n 1 - Delete subscription \n 2 - Add subscription \n 3 - Logout")
            value = int(input())
            while(value not in [1, 2, 3]):
                print("[bold underline]Invalid option![/bold underline]")
                value = int(input())
            
            if value == 1:
                self.delSubscription(server)
                os.system('cls')
            elif value == 2:
                os.system('cls')
                self.addSubscription(server)
                os.system('cls')
            elif value == 3:
                os.system('cls')
                return 0

    @Pyro4.expose
    def notifyAvailableDriver(self, name, contact):
        """
        Description: method called by the server whenever a request subscription
                     from the client is met at the host, thus notifying the user.
        
        Parameters:
        - name (string): name of the OTHER client/user that meets one of THIS
                         client's request subscriptions;
        - contact (string): contact of the OTHER client/user that meets one
                            of THIS client's request subscriptions.

        Returns:
        - None
        """
        console = Console()
        print("\n[bold]NOTIFICATION ON [/bold]", end="")
        console.print(self.name, style="bold orange3", end="")
        print(": Available ride from ")
        console.print(name, style="bold magenta", end="")
        print(" and contact: ")
        console.print(contact, style="bold magenta", end="")


    @Pyro4.expose
    def notifyAvailablePassenger(self, name, contact):
        """
        Description: method called by the server whenever a ride subscription
                     from the client is met at the host, thus notifying the user.
        
        Parameters:
        - name (string): name of the OTHER client/user that meets one of THIS
                         client's ride subscriptions;
        - contact (string): contact of the OTHER client/user that meets one
                            of THIS client's ride subscriptions.

        Returns:
        - None
        """
        console = Console()
        print("\n[bold]NOTIFICATION ON [/bold]", end="")
        console.print(self.name, style="bold orange3", end="")
        print(": Available passenger ")
        console.print(name, style="bold magenta", end="")
        print(", contact: ")
        console.print(contact, style="bold magenta", end="")


class Interface():
    """
    Description: this class implements a simple interaction with the user through
                 the terminal. The methods follow a menu to menu structure
                 specified by this diagram: -TODO- LINK.
    
    Attributes:
    - state (int): current state of the interface, determining which menu to display
                   0 - main menu
                   1 - login menu
                   2 - client register menu
                   3 - client based menu interaction with application functionalities
                   9 - exits the application;
    - clients (list of Client): keeps track of the registered clients; -TODO- MAYBE USE THE SERVER TO GET THE LIST OF CLIENTS
    - current_client (Client): currently active client.
        
    Methods:
    - setState: update method for the self.state attribute;
    - getClient: consults the list of clients for a given client;
    - mainMenu: main menu method with user interaction through the terminal;
    - loginMenu: login menu method with user interaction through the terminal;
    - registerMenu: client register menu method with user interaction through
                    the terminal;
    - clientMenu: client menu method which interacts with the self.current_client
                  attribute.
    """

    def __init__(self):
        self.state = 0
        self.clients = []
        self.current_client = None
        os.system('cls')

    def setState(self, value):
        self.state = value


    def getClient(self, email, password):
        """
        Description: auxiliary function to retrieve a Client from the clients list
                     given their email and password.
        
        Parameters:
        - email: client email;
        - password: client password.

        Returns:
        - (Client): returns the Client object if it is in the list, if not, return None.
        """
        return next((client for client in self.clients if client.contact == email), None) 


    def mainMenu(self):
        """
        Description: main menu function, not yet related to a specific Client.
                     Introduces the application and asks the user to choose the
                     next action. This structure (question and answer) will be
                     used for the following menus. Additionally, the self.state
                     attribute will be updated accordingly, serving as the
                     return of the function.
        
        Parameters:
        - None

        Returns:
        - None
        """
        print(" ---- [bold]Welcome to [red]RideTogether![/red][/bold] ----")
        print("Are you already a user? Want to login or register?")
        print("Text in this [bold bright_cyan]color[/bold bright_cyan] represent options to be selected!\n 1 - Login \n 2 - Register\n 9 - Exit")
        self.state = int(input())
        os.system('cls')
    

    def loginMenu(self):
        """
        Description: login menu function, prompts the user for credentials to login.
        
        Parameters:
        - None

        Returns:
        - None
        """
        print(" ------ [bold] Login [/bold] ------")
        print("Log into your account with your email and password.\n"
              " [bold bright_cyan]Email[/bold bright_cyan]: ", end="")
        email = input()
        print(" [bold bright_cyan]Password[/bold bright_cyan]: ", end="")
        password = stdiomask.getpass(prompt="")

        client = self.getClient(email, password)
        if client == None:
            print("User not found! Please try again...\n 1 - Login \n 0 - Main menu")
            self.state = int(input())
        else:
            console = Console()
            print("\nWelcome ", end="")
            console.print(client.name, style="bold orange3", end="")
            print("!\nLogging in...")
            self.current_client = client
            self.state = 3
            time.sleep(2)
        
        os.system('cls')


    def registerMenu(self, server):
        """
        Description: client register menu function, prompts the user for name,
                     email and password to register them in the application.
        
        Parameters:
        - None

        Returns:
        - None
        """
        print(" ------ [bold] Register [/bold] ------")
        print("To become a user of [bold red]RideTogether![/bold red], "
              "first type in your name.\n [bold bright_cyan]Name[/bold bright_cyan]: ", end="")
        name = input()
        print("\nNext step, your email.\n [bold bright_cyan]Email[/bold bright_cyan]: ", end="")
        email = input()
        print("\nFinally, choose a password for your account.\n [bold bright_cyan]Password[/bold bright_cyan]: ", end="")
        password = stdiomask.getpass(prompt="")
        os.system('cls')
        
        self.clients.append(Client(name, email, password))
        self.clients[-1].registerInServer(server)

        print("\n 0 - Return to main menu")
        self.state = int(input())
        
        os.system('cls')
        

    def clientMenu(self, server):
        """
        Description: client menu function to simply call the correct client's
                     method.
        
        Parameters:
        - None

        Returns:
        - None
        """
        self.state = self.current_client.interact(server)
        self.current_client = None


def main():
    # Pyro exceptions
    sys.excepthook = Pyro4.util.excepthook
    
    # Server proxy from Server class in server.py
    # nameserver = Pyro4.locateNS()
    # server = Pyro4.Proxy(nameserver.lookup("server"))
    
    server = Pyro4.Proxy("PYRONAME:rt.server")

    interface = Interface()
    while(interface.state != 9):
        if interface.state == 0:
            interface.mainMenu()
        elif interface.state == 1:
            interface.loginMenu()
        elif interface.state == 2:
            interface.registerMenu(server)
        elif interface.state == 3:
            if interface.current_client != None:
                interface.clientMenu(server)
        elif interface.state != 9:
            os.system('cls')
            interface.setState(0)
            print("[bold underline]Invalid option![/bold underline] "
                  "Please select one of the shown numbers.\n")


if __name__=="__main__":
    main()