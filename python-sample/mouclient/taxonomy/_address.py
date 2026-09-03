from rdflib.namespace import Namespace
from rdflib.term import URIRef

class Address:
    _NS = Namespace("https://data.gov.sk/def/address-type/")

    # https://metais.vicepremier.gov.sk/refid/set/codelist/CL010139?page=1&count=20&sorting%5Bcode%5D=asc
    PermanentAddress:URIRef = _NS["100001"]
