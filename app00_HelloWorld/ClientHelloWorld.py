import Pyro4

# Tive que fazer em portugues por causa do passo a passo rs :D 

# 2 - Criar pacote hello world ????

# 4 - Criar interface para o cliente
# Extends remote function
# Interface with @Pyro4.expose can be called from outside 
@Pyro4.expose
class InterfaceCli():
    def __init__(self):
        self.local = "cliente"

    def notificar(texto):
        print ("Notificando")
