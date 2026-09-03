from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class ADMS(DefinedNamespace):

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    identifier: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    Identifier: URIRef

    _NS = Namespace("http://www.w3.org/ns/adms#")
