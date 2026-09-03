from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class PERSON(DefinedNamespace):

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    birthName: URIRef
    placeOfBirth: URIRef
    residency: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class

    _NS = Namespace("http://www.w3.org/ns/person#")
