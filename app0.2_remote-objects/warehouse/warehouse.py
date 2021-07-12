from __future__ import print_function
import Pyro4

# Start name server
## python -m Pyro4.naming
# Check NS list 
## python -m Pyro4.nsc list

# Expose class
@Pyro4.expose
# Required to properly have a persistent warehouse inventory)
@Pyro4.behavior(instance_mode="single")        
class Warehouse(object):
    def __init__(self):
        self.contents = ["chair", "bike", "flashlight", "laptop", "couch"]

    def list_contents(self):
        return self.contents

    def take(self, name, item):
        self.contents.remove(item)
        print("{0} took the {1}.".format(name, item))

    def store(self, name, item):
        self.contents.append(item)
        print("{0} stored the {1}.".format(name, item))

def main():
    # Registering Pyro class as a daemon in name server
    Pyro4.Daemon.serveSimple(
            {
                Warehouse: "example.warehouse"
            },
            ns = True)

if __name__=="__main__":
    main()