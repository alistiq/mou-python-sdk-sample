from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class PPER(DefinedNamespace):

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    birthNumberCode: URIRef
    dateOfBirth: URIRef
    yearOfBirth: URIRef

    hasCivilDisability: URIRef
    namePrefix: URIRef
    nameSuffix: URIRef
    sex: URIRef

    maritalStatusType: URIRef
    personRelationship: URIRef
    relatedPerson: URIRef
    marriageCertificate: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    PhysicalPerson: URIRef
    NamePrefix: URIRef
    NameSuffix: URIRef
    Sex: URIRef
    MaritalStatusType: URIRef
    MarriageCertificate: URIRef
    PersonRelationship: URIRef


    _NS = Namespace("https://data.gov.sk/def/ontology/physical-person/")
