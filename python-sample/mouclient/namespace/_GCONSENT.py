from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class GCONSENT(DefinedNamespace):

    """
    W3.org GConsent vocabulary

    NOT an extensive list of properties and classes for GConsent vocab.
    Only props used in MOU project are listed.

    """

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    providedConsent: URIRef
    forPersonalData: URIRef
    hasStatus: URIRef
    isProvidedTo: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    ConsentStatusRequested: URIRef
    ConsentStatusExplicitlyGiven: URIRef


    _NS = Namespace("https://w3id.org/GConsent#")
