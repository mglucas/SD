from __future__ import print_function
import Pyro4
import Pyro4.util
import sys

if sys.version_info < (3, 0):
    input = raw_input

sys.excepthook = Pyro4.util.excepthook

# Instance
serverUser = Pyro4.Proxy("PYRONAME:server.user")

User = serverUser("123")
User = serverUser.register("Jonas","3412","kkk")

print (User.name)