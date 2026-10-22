"""Service SOAP avec Spyne - COMPLETE."""
from wsgiref.simple_server import make_server
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Float, Fault
from spyne.model.complex import ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

import db

TNS = "http://bibliotech.example/soap"


class BookModel(ComplexModel):
    __namespace__ = TNS
    id = Integer
    title = Unicode
    author = Unicode
    available_copies = Integer
    rental_price = Float


def guard(func, *args):
    """Appelle func(*args) ; transforme ValueError et LookupError en Fault SOAP."""
    try:
        return func(*args)
    except ValueError as e:
        raise Fault("Client.ValidationError", str(e))
    except LookupError as e:
        raise Fault("Client.NotFoundError", str(e))


class BookService(ServiceBase):
    
    @rpc(Integer, Unicode, Unicode, Integer, Float, _returns=Unicode)
    def CreateBook(ctx, id, title, author, available_copies, rental_price):
        guard(db.create_book, id, title, author, available_copies, rental_price)
        return f"Succès : Livre '{title}' ajouté avec l'ID {id}."

    @rpc(Integer, _returns=BookModel)
    def GetBook(ctx, id):
        book_dict = guard(db.get_book, id)
        return BookModel(**book_dict)

    @rpc(Integer, Unicode, Unicode, Integer, Float, _returns=Unicode)
    def UpdateBook(ctx, id, title, author, available_copies, rental_price):
        guard(db.update_book, id, title, author, available_copies, rental_price)
        return f"Succès : Livre ID {id} mis à jour avec succès."

    @rpc(Integer, _returns=Unicode)
    def DeleteBook(ctx, id):
        guard(db.delete_book, id)
        return f"Succès : Livre ID {id} supprimé avec succès."


application = Application([BookService], 
                          tns=TNS, 
                          in_protocol=Soap11(validator='lxml'), 
                          out_protocol=Soap11())

if __name__ == "__main__":
    # Initialiser la base de données
    db.init_db()
    
    # Lancer le serveur
    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    print("Service SOAP en cours d'exécution sur http://localhost:8000")
    print("WSDL disponible sur http://localhost:8000/?wsdl")
    server.serve_forever()