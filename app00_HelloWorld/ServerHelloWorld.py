import Pyro4

# Tive que fazer em portugues por causa do passo a passo rs :D 

# 2 - Criar pacote hello world ????

# 3 - Create interface for Server
# Extends remote function
# Interface with @Pyro4.expose can be called from outside 
@Pyro4.expose
class InterfaceServ():
    def __init__(self):
        self.local = "server"

    def registrarInteresse(texto,referenciaCliente):
        print("Registro de interesse!")

class ServImpl():
    def __init__(self):
        self.local = "servente"



def main():
    Pyro4.Daemon.serveSimple(
            {
                InterfaceServ: "Servidor"
            },
            ns = True)

if __name__=="__main__":
    main()