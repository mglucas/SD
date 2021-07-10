import Pyro4
import random

# Start name server
## python -m Pyro4.naming
# Check NS list 
## python -m Pyro4.nsc list

# @Pyro4.expose      
class Server(object):
    def __init__(self):
        print ("server ok")
        self.clients = []
        self.rides = []
        self.requests = []
        self.current_id = 0
       
    def addClient(self, name, contact, public_key):
        self.clients.append({
            "name" : name,
            "contact" : contact,
            "publickey" : public_key
        })

    def addRideRequest(self, object, name, origin, destination, date):
        self.current_id += 1
        self.requests.append({
            "id" : self.current_id,
            "object" : object,
            "name": name,
            "origin" : origin,
            "destination" : destination,
            "date" : date
        }) 

        return self.current_id

    def addRide(self, object, name, origin, destination, date, n_passengers):
        self.current_id += 1
        self.rides.append({
            "id" : self.current_id,
            "object" : object,
            "name": name,
            "origin" : origin,
            "destination" : destination,
            "date" : date,
            "passengers" : n_passengers
        })  

        return self.current_id

    def delRideRequest(self, id ):
        del_request = next(req for req in self.requests if req["id"] == id )
        self.requests.remove(del_request)

    def delRide(self):
        del_ride = next(ride for ride in self.rides if ride["id"] == id )
        self.rides.remove(del_ride)

    def getAvailableRides(self,origin,destination,date):
        return [ride for ride in self.rides if (ride["origin"] == origin 
                                            and ride["destination"] == destination 
                                            and ride["date"] == date)]

def main():
    print("main")
    # Registering Pyro class as a daemon in name server
    # Pyro4.Daemon.serveSimple(
    #         {
    #             User: "server.user"
    #         },
    #         ns = True)

if __name__=="__main__":
    main()