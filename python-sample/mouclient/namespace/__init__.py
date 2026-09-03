from rdflib import Namespace
from mouclient.namespace._GCONSENT import GCONSENT
from mouclient.namespace._W3_CREDENTIALS import W3_CREDENTIALS
from mouclient.namespace._W3_ACL import W3_ACL
from mouclient.namespace.ADMS import ADMS
from mouclient.namespace.PERSON import PERSON
from mouclient.namespace.PPER import PPER
from mouclient.namespace.LOCA import LOCA
from mouclient.namespace._MOUVC import MOUVC

SCHEMA = Namespace("http://schema.org/")

ISVS = Namespace("https://data.gov.sk/id/egov/isvs/")

RFOCODELIST = Namespace("https://rfo.gov.sk/set/codelist/")
RFOCOLOR = Namespace("https://rfo.gov.sk/set/rfocolor/")
RFOADDRESS = Namespace("https://rfo.gov.sk/id/physical-address/")
RFOSTREET = Namespace("https://rfo.gov.sk/id/street/")
RFOPERSON = Namespace("https://rfo.gov.sk/id/person/")

__all__ = [
    "GCONSENT",
    "W3_CREDENTIALS",
    "W3_ACL",
    "ADMS",
    "PERSON",
    "PPER",
    "LOCA",
    "MOUVC",
    "SCHEMA",
    "ISVS",
    "RFOCODELIST",
    "RFOCOLOR",
    "RFOADDRESS",
    "RFOSTREET",
    "RFOPERSON",
]
