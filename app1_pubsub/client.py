import Pyro4
import Pyro4.util
import sys
from server import Server

# sys.excepthook = Pyro4.util.excepthook

# Instance
# serverUser = Pyro4.Proxy("PYRONAME:server.user")

class Client(object):
    def __init__(self, name, contact):
        self.name = name
        self.contact = contact
        # Private and public keys
        self.priv_key = 1
        self.pub_key = 2

    def registerInServer(self, server):
        print(f"this is {self.name} registering in server.")        
        server.addClient(self.name,self.contact,self.pub_key)

    def interact(self, server):
        print("")
        print("Are you a driver or a passenger?")        
        value = input("1 - Driver \n 2 - Passenger")

        if value == 1:
            print("As a driver:")
        elif value == 2:
            print("As a passenger:")
        else: 
            print("Invalid option.")

    def notifyAvailableRide(self, name, contact):
        print(f"Available Ride from {name} and contact: {contact}")

    def notifyAvailablePassenger(self, name, contact):
        print(f"Available Passenger: {name}, contact: {contact}")

def main():
    server = Server() 
    joao = Client("Joao","123")
    maria = Client("Maria","123123")
    athena = Client("Athena","bumbum")

    # Register 



if __name__=="__main__":
    main()