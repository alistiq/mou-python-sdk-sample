from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef


class LOCA(DefinedNamespace):

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    district: URIRef
    issuedAt: URIRef
    lau1: URIRef
    lau2: URIRef
    nuts3: URIRef
    orientationNumber: URIRef
    propertyRegistrationNumber: URIRef
    buildingPart: URIRef
    street: URIRef
    unCountry: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    District: URIRef
    LAU1: URIRef
    LAU2: URIRef
    NUTS3: URIRef
    Location: URIRef
    PhysicalAddress: URIRef
    Street: URIRef
    UNCountry: URIRef

    _NS = Namespace("https://data.gov.sk/def/ontology/location/")
