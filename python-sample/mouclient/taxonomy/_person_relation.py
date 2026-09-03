from rdflib.namespace import Namespace
from rdflib.term import URIRef

class PersonRelation:
    _NS = Namespace("https://data.gov.sk/def/person-relationship-type/")

    # https://metais.vicepremier.gov.sk/codelists/detail/2946?page=1&count=20&sorting%5Bcode%5D=asc
    Offspring: URIRef = _NS["03"]
