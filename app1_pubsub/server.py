from __future__ import print_function
import Pyro4
import random

# Start name server
## python -m Pyro4.naming
# Check NS list 
## python -m Pyro4.nsc list

@Pyro4.expose      
class User(object):
    def __init__(self,userId):
        self.userID = userId

    @property
    def userID(self):
        return self.userID

    def register(self,name,phoneNumber,publicKey):
        self.name = name
        self.phoneNumber = phoneNumber
        self.publicKey = publicKey 

    def search(self,origin,destination):
        print("Origin:", origin)
        print("Destination:",destination)

def main():
    # Registering Pyro class as a daemon in name server
    Pyro4.Daemon.serveSimple(
            {
                User: "server.user"
            },
            ns = True)

if __name__=="__main__":
    main()