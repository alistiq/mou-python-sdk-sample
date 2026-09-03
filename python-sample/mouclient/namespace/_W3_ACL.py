from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class W3_ACL(DefinedNamespace):

    """
    W3.org Basic Access Control ontology

    Defines the class Authorization and its essential properties,
    and also some classes of access such as read and write.

    NOT an extensive list of properties and classes for ACL vocab.
    Only props used in MOU project are listed.

    """

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    mode: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    Read: URIRef
    Write: URIRef
    Append: URIRef


    _NS = Namespace("http://www.w3.org/ns/auth/acl#")
