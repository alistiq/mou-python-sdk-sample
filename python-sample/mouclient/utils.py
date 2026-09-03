import arrow

from typing import Callable, Iterable, TypeVar, Any
from rdflib import RDF, SKOS, Graph, IdentifiedNode, BNode, Literal
from rdflib.term import Identifier
from mouclient.api.service.exceptions import InvalidWebIdError

_S = TypeVar("_S")
_T1 = TypeVar("_T1")

def parse_datetime(dt: Any) -> Any:
    return arrow.get(dt).datetime if isinstance(dt, str) else dt

def bearer_auth(token: str) -> str:
    return f"Bearer {token}"

def dpop_auth(token: str) -> str:
    return f"DPoP {token}"

# e.g. https://your-mou-host.example.com:3000/someholder/profile/card#me
# where 'someholder' is what we understand as a POD
def web_id_to_pod(web_id: str) -> str:
    parts = web_id.split("/")
    if len(parts) < 4:
        raise InvalidWebIdError(f"{web_id} is not a valid webId format!")
    return parts[3]

def pod_to_web_id(holder: str, base_pod_uri: str) -> str:
    return f"{base_pod_uri}{holder}/profile/card#me"

def resource_name_from_uri(uri: str) -> str:
    try:
        last_component = uri.rsplit("/", 1)[1]
        return last_component
    except IndexError:
        return uri

def rdf_collection_to_list(graph: Graph, entry: Identifier) -> (list):
    ret = list()
    current = entry
    # not a collection entry point
    if entry is not None and not isinstance(entry, BNode):
        ret.append(entry)
        return ret

    # empty list
    if entry is None or graph.value(entry, RDF.first, None) is None or graph.value(entry, RDF.first, None) == RDF.nil:
        return ret

    while current != RDF.nil:
        ret.append(graph.value(current, RDF.first, None))
        current = graph.value(current, RDF.rest, None)

    return ret

def map_join(__func: Callable[[_T1], _S], __iter1: Iterable[_T1], glue: str) -> str:
    return glue.join( map(__func, __iter1) )

def pref_label(graph: Graph, node:IdentifiedNode, lang: str = "en") -> str:
    # no labels for "not found" nodes
    if node is None: return None
    labels = graph.objects(node, SKOS.prefLabel)
    for l in labels:
        if isinstance(l, Literal) and l.language == lang: return l.value
    return ""

def pref_labels(graph: Graph, nodes:Iterable[IdentifiedNode], lang:str = "en") -> list:
    # no labels for "not found" nodes
    if nodes is None: return None
    ret = []
    for node in nodes:
        label = pref_label(graph, node, lang)
        if label: ret.append(label)
    return ret

def literal_value(literal: Literal) -> Any:
    if isinstance(literal, Literal):
        return literal.value

    return None
