from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class W3_CREDENTIALS(DefinedNamespace):

    """
    W3.org Credentials vocabulary

    NOT an extensive list of properties and classes for Credentials vocab.
    Only props used in MOU project are listed.

    """

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    credentialStatus: URIRef
    credentialSubject: URIRef
    issuanceDate: URIRef
    issuer: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    VerifiableCredential: URIRef


    _NS = Namespace("https://www.w3.org/2018/credentials#")
