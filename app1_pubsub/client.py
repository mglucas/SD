# -*- coding: utf-8 -*-
"""
Created on July 10 2021

@authors: Lucas Ricardo Marques de Souza
          Victor Feitosa Lourenco

This python script was created for the Distribuited Systems course for the
Computer Engineering major at the Federal University of Technology - Parana.
"""

""" --------- IMPORTS --------- """
# Libraries
import os
import sys
import time
import Pyro4
import Pyro4.util
from rich import console
import stdiomask
from rich import print
from rich.console import Console
from prettytable import PrettyTable

# Internal Modules
from server import Server
""" ------------------------ """

# sys.excepthook = Pyro4.util.excepthook

# Instance
# serverUser = Pyro4.Proxy("PYRONAME:server.user")

class Client(object):
    """
    Description: this class implements the client user functionalities.
                 It includes management of it's attributes, exchanges with
                 the server and terminal user interface interaction.
    
    Attributes:
    - name (str): name of the client only set on creation;
    - contact (str): contact of the client (email) only set on creation;
    - password (str): client password.
    - priv_key -TODO- FINISH THIS
    - pub_key 
    - object  
        
    Methods:
    - d: ;
    - a: .
    """

    def __init__(self, name, contact, password):
        self.name = name
        self.contact = contact
        self.password = password
        # Private and public keys
        self.priv_key = 1
        self.pub_key = 2
        self.object = 1

    def registerInServer(self, server):
        print(f"This is {self.name} registering in server.")        
        server.addClient(self.name,self.contact,self.pub_key)

    def displaySubscriptions(self, processes):
        requests_table = PrettyTable()
        rides_table = PrettyTable()

        print(" - Want to be a passenger:")
        if processes[0] == []:
            print("\tNot subscribed to any rides yet!")
        else:
            requests_table.field_names = ["ID", "Origin", "Destination", "Date"]
            for request in processes[0]:
                requests_table.add_row([request.id, request.origin,
                                        request.destination, request.date])
        
        print("\n - Want to be a driver:")
        if processes[1] == []:
            print("\tNot subscribed to any rides yet!")
        else:
            rides_table.field_names = ["ID", "Origin", "Destination", "Date", "Passengers"]
            for ride in processes[1]:
                rides_table.add_row([ride.id, ride.origin, ride.destination,
                                     ride.date, ride.passengers])

    def delSubscription(self, server):
        pass

    def addSubscription(self, server):
        print("Do you want to be a driver or a passenger?")
        value = int(input(" 1 - Driver \n 2 - Passenger \n 3 - Return to user menu"))
        while(value not in [1, 2, 3]):
            print("[bold underline]Invalid option![/bold underline]")
            value = int(input())
        
        if value == 1:
            print("OK! We need to know a few things about the ride you want to give.")
            origin = input(" Origin location: ")
            dest = input(" Destination location: ")
            date = input(" Date of the ride: ")
            n_pass = int(input(" Max number of passengers: "))

            server.addRide(self.object, self.name, origin, dest, date, n_pass)
            print("New subscription successfully added! Returning to user menu...")
            time.sleep(2)
        
        elif value == 2:
            print("OK! We need to know a few things about the ride you want to take.")
            origin = input(" Origin location: ")
            dest = input(" Destination location: ")
            date = input(" Date of the ride: ")

            server.addRideRequest(self.object, self.name, origin, dest, date)
            print("New subscription successfully added! Returning to user menu...")
            time.sleep(2)


    def interact(self, server):
        while True:
            console = Console()
            print("\tHello ", end="")
            console.print(self.name, style="bold orange3", end="")
            print("! These are your active subscriptions:")
            
            subs = server.getClientSubscriptions(self.object)
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

    def notifyAvailableRide(self, name, contact):
        print(f"NOTIFICATION: Available Ride from {name} and contact: {contact}")

    def notifyAvailablePassenger(self, name, contact):
        print(f"NOTIFICATION: Available Passenger: {name}, contact: {contact}")


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
    - details: returns a string containing the information of the dataset;
    - append_exception: append original column name to exceptions;
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
        Description: main menu function, not yet related to a specific Client. Introduces
                     the application and asks the user to choose the next action. This
                     structure (question and answer) will be used for the following menus.
                     Additionally, the self.state attribute will be updated accordingly,
                     serving as the return of the function.
        
        Parameters:
        - None

        Returns:
        - None
        """
        print(" ---- [bold]Welcome to [red]RideTogether![/red][/bold] ----")
        print("Are you already a user? Login by typing 1!")
        print("If not, type 2 to register now!\n 1 - Login \n 2 - Register\n 9 - Exit")
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
        print("Log into your account with your email and password!")
        email = input("Email: ")
        password = stdiomask.getpass()
        client = self.getClient(email, password)

        if client == None:
            print("User not found! Please try again...\n 1 - Login \n 0 - Main menu")
            self.state = int(input())
        else:
            console = Console()
            print("\nWelcome ", end="")
            console.print(client.name, style="bold orange3", end="")
            print("!\nLogging in...\n\n")
            self.current_client = client
            self.state = 3
            time.sleep(2)
        
        os.system('cls')


    def registerMenu(self):
        """
        Description: client register menu function, prompts the user for name, email and
                     password to register them in the application.
        
        Parameters:
        - None

        Returns:
        - None
        """
        print("To become a user of [bold red]RideTogether![/bold red], first type in your name.")
        name = input(" Name: ")
        print("\n Next step, your email.")
        email = input("Email: ")
        print("\n Finally, choose a password for your account.")
        password = stdiomask.getpass()

        self.clients.append(Client(name, email))

        console = Console()
        print("\nYou were registered successfully, ", end="")
        console.print(name, style="bold orange3", end="")
        print("!\n 0 - Return to main menu")
        self.state = int(input())
        
        os.system('cls')
        

    def clientMenu(self, server):
        """
        Description: client menu function to simply call the correct client's method.
        
        Parameters:
        - None

        Returns:
        - None
        """
        self.state = self.current_client.interact(server)
        self.current_client = None


def main():
    server = Server() 
    # joao = Client("Joao","123")
    # maria = Client("Maria","123123")
    # athena = Client("Athena","bumbum")

    interface = Interface()
    while(interface.state != 9):
        if interface.state == 0:
            interface.mainMenu()
        elif interface.state == 1:
            interface.loginMenu()
        elif interface.state == 2:
            interface.registerMenu()
        elif interface.state == 3:
            interface.clientMenu(server)
        elif interface.state != 9:
            os.system('cls')
            interface.setState(0)
            print("[bold underline]Invalid option![/bold underline] Please select one of the shown numbers.\n")


if __name__=="__main__":
    main()