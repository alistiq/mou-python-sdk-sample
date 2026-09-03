import typing
import json
import arrow
from os import getenv
from types import TracebackType
from datetime import date
from typing import Optional
from dotenv import load_dotenv

from rdflib import Dataset, Graph, IdentifiedNode, URIRef
from rdflib.namespace import DCTERMS, FOAF, SKOS, RDF

from mouclient.mou_client import MouClient
from mouclient.api.service.vc_service import Mode, UsageLimit
from mouclient.namespace import ADMS, LOCA, PERSON, PPER, ISVS, RFOPERSON, SCHEMA
from mouclient.taxonomy import Address
from mouclient.utils import map_join, pref_label, rdf_collection_to_list, literal_value

from exceptions import AddressNotFoundError, NoGrantError

U = typing.TypeVar("U", bound="MouRepository")
class Person:
    def __init__(
        self,
        id: Optional[str] = None,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        birth_name: Optional[str] = None,
        name_prefix: Optional[str] = None,
        name_suffix: Optional[str] = None,
        birth_date: Optional[date] = None,
        birth_number: Optional[str] = None
    ) -> None:
        self.id = id
        self.given_name = given_name
        self.family_name = family_name
        self.birth_name = birth_name
        self.name_prefix = name_prefix
        self.name_suffix = name_suffix
        self.birth_date = birth_date
        self.birth_number = birth_number

    @classmethod
    def from_graph(cls, graph: Graph, subject: URIRef, lang:str):
        # the ID of the person for our purposes will be the slug in URI
        # that can identify the person as a subject in the graph
        id = subject.replace(RFOPERSON, "")
        given_name = graph.value(subject, FOAF.givenName, None)
        given_name_list = rdf_collection_to_list(graph, given_name)
        family_name = graph.value(subject, FOAF.familyName, None)
        family_name_list = rdf_collection_to_list(graph, family_name)
        birth_name = graph.value(subject, PERSON.birthName, None)
        birth_name_list = rdf_collection_to_list(graph, birth_name)
        name_prefixes = graph.objects(subject, PPER.namePrefix)
        name_suffixes = graph.objects(subject, PPER.nameSuffix)
        birth_date_str = graph.value(subject, PPER.dateOfBirth, None)
        birth_date = date.fromisoformat(birth_date_str) if birth_date_str else None
        birth_number = literal_value(graph.value(subject, PPER.birthNumberCode, None))

        return Person(
            id=id,
            given_name=' '.join(given_name_list),
            family_name=' '.join(family_name_list),
            birth_name=' '.join(birth_name_list),
            name_prefix=map_join(lambda node: pref_label(graph, node, lang), name_prefixes, ", "),
            name_suffix=map_join(lambda node: pref_label(graph, node, lang), name_suffixes, ", "),
            birth_date=birth_date,
            birth_number=birth_number
        )

    def __str__(self):
        # the complicated expression is to represent dictionary values with str() method
        # cause default in python is with repr() which won't print the nested objects nicely
        return f"<{self.__class__.__name__}:" + " {%s}"%', '.join("%r: %s"%p for p in self.__dict__.items()) + ">"


class PhysicalAddress:
    def __init__(
        self,
        street: Optional[str] = None,
        property_registration_number: Optional[str] = None,
        orientation_number: Optional[str] = None,
        district: Optional[str] = None,  # cast obce (part of municipality)
        lau2: Optional[str] = None,  # obec (municipality)
        lau1: Optional[str] = None,  # okres (district)
        nuts3: Optional[str] = None,  # kraj (region)
        flat_number: Optional[str] = None,  # cislo bytu (flat number)
    ) -> None:
        self.street = street
        self.property_registration_number = property_registration_number
        self.orientation_number = orientation_number
        self.district = district
        self.lau2 = lau2
        self.lau1 = lau1
        self.nuts3 = nuts3
        self.flat_number = flat_number

    @classmethod
    def from_graph(cls, graph: Graph, subject: URIRef, lang: str):
        street = pref_label(graph, graph.value(subject, LOCA.street, None), lang=lang)
        reg_number = literal_value(graph.value(subject, LOCA.propertyRegistrationNumber, None))
        orientation_number = literal_value(graph.value(subject, LOCA.orientationNumber, None))
        district = pref_label(graph, graph.value(subject, LOCA.district, None), lang=lang)
        city = pref_label(graph, graph.value(subject, LOCA.lau2, None), lang=lang)
        county = pref_label(graph, graph.value(subject, LOCA.lau1, None), lang=lang)
        region = pref_label(graph, graph.value(subject, LOCA.nuts3, None), lang=lang)
        # building part??
        flat_number = graph.value(subject, LOCA.buildingPart, None)
        return PhysicalAddress(
            street=street,
            property_registration_number=reg_number,
            orientation_number=orientation_number,
            district=district,
            lau2=city,
            lau1=county,
            nuts3=region,
            flat_number=flat_number
        )

    def __str__(self):
        # the complicated expression is to represent dictionary values with str() method
        # cause default in python is with repr() which won't print the nested objects nicely
        return f"<{self.__class__.__name__}:" + " {%s}"%', '.join("%r: %s"%p for p in self.__dict__.items()) + ">"


class ResidencyPersonalData:
    def __init__(self, holder: Person, address: PhysicalAddress) -> None:
        self.holder = holder
        self.address = address

    def __str__(self):
        # the complicated expression is to represent dictionary values with str() method
        # cause default in python is with repr() which won't print the nested objects nicely
        return f"<{self.__class__.__name__}:" + " {%s}"%', '.join("%r: %s"%p for p in self.__dict__.items()) + ">"

class ChildResidencyPersonalData:
    def __init__(self, parent: Person, child: Person, address: PhysicalAddress) -> None:
        self.parent = parent
        self.child = child
        self.address = address

    def __str__(self):
        # the complicated expression is to represent dictionary values with str() method
        # cause default in python is with repr() which won't print the nested objects nicely
        return f"<{self.__class__.__name__}:" + " {%s}"%', '.join("%r: %s"%p for p in self.__dict__.items()) + ">"


class MouRepository:

    dataset_resources = [
        "informacie-o-fo-z-rfo_identifikator-osoby",
        "informacie-o-fo-z-rfo_meno-a-priezvisko",
        "informacie-o-fo-z-rfo_adresy-pobytu",
        "informacie-o-fo-z-rfo_rodinne-vztahy",
        "informacie-o-fo-z-rfo_narodenie"
    ]

    def __init__(self, lang:str = "en") -> None:
        # service configuration from environment variables
        # before MouClient init
        load_dotenv(dotenv_path=".env", verbose=True, override=True)
        self.client = MouClient()
        self.lang = lang
        self.pod_name = getenv("MOU_USER_NAME")
        self.rfo_graph = None

    async def close(self) -> None:
        """Call explicit close when finishing work with the client
        to properly close all network clients
        """
        await self.client.close()

    async def __aenter__(self: U) -> U:
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[typing.Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)

    async def has_service_dataset_access(self) -> bool:
        grant = await self.get_service_dataset_access_grant()
        return grant is not None

    async def get_service_dataset_access_grant(self) -> Optional[str]:
        return await self.client.get_valid_dataset_access_grant(
            holder_username=self.pod_name,
            resource_names=MouRepository.dataset_resources,
            modes=[Mode.READ],
            usageLimit=UsageLimit.AFTER_CHANGE
        )

    async def request_service_dataset_access(self) -> None:
        await self.client.request_dataset_access(
            holder_username=self.pod_name,
            resource_names=MouRepository.dataset_resources,
            notification_subject="Žiadosť o prístup k dátam",
            modes=[Mode.READ],
            usageLimit=UsageLimit.AFTER_CHANGE
        )

    async def await_dataset_access(self) -> Optional[str]:
        return await self.client.await_dataset_access(
            holder_username=self.pod_name,
            resource_names=MouRepository.dataset_resources,
            modes=[Mode.READ]
        )

    async def load_rfo_graph(self) -> Graph:
        dataset = Dataset()

        grant = await self.get_service_dataset_access_grant()
        if not grant:
            raise NoGrantError("No grant to access personal data, cannot proceed.")

        consent_token = await self.client.perform_consent_token_request(grant)

        for res in MouRepository.dataset_resources:
            content = await self.client.get_dataset_resource(self.pod_name, res, consent_token.access_token)
            # we should work with RDF graph, but mou-common don't define all props yet
            # we will work with json/dict instead
            resource = json.loads(content)
            protected = resource["metadata"]["protectedDataset"]

            payload = await self.client.decrypt_resource(protected, walletPassword=getenv("MOU_WALLET_PASSWORD", ""))

            dataset.parse(data=payload, format="json-ld")


        # named graph with isvs ID of Register of Physical Person
        self.rfo_graph = dataset.get_graph(ISVS["191"])
        return self.rfo_graph


    ##
    # Does all the heavy lifting to load and extract data needed for permanent residency
    # form from users POD.
    # The access consent must already be granted, otherwise the operation fails.
    ##
    async def extract_personal_data_for_residency(self) -> ResidencyPersonalData:
        if not self.rfo_graph:
            graph = await self.load_rfo_graph()
        else:
            graph = self.rfo_graph

        p_id_ref = self._detect_owner_id(graph)
        holder = Person.from_graph(graph, p_id_ref, self.lang)

        # find permanent address node for holder
        address_ref = self._find_valid_permanent_address(graph, p_id_ref)
        if address_ref is None: raise AddressNotFoundError("Unable to identify valid permanent address in personal data.")
        address = PhysicalAddress.from_graph(graph, address_ref, self.lang) if address_ref else None

        return ResidencyPersonalData(holder=holder, address=address)


    def _detect_owner_id(self, graph: Graph) -> Optional[URIRef]:
        # first let's identify the ID of a person, this dataset belongs to
        # because the dataset may contain multiple PhysicalPerson records (related)
        # NOTE: this way may not be reliable in case related persons would also have Identifier triples
        p_id_node = graph.value(None, RDF.type, ADMS.Identifier)
        p_id = graph.value(p_id_node, SKOS.notation, None)
        # construct the qualified id ref
        return RFOPERSON[p_id] if p_id else None

    def _find_valid_permanent_address(self, graph: Graph, person: IdentifiedNode) -> Optional[IdentifiedNode]:
        for address in graph.objects(person, PERSON.residency):
            # if valid date is missing, consider valid

            valid_from_v = graph.value(address, SCHEMA.validFrom, None)
            valid_from = arrow.get(valid_from_v) if valid_from_v else arrow.get(1970,1,1)

            valid_until_v = graph.value(address, SCHEMA.validUntil, None)
            valid_until = arrow.get(valid_until_v) if valid_until_v else arrow.get(2300,1,1)

            address_type = graph.value(address, DCTERMS.type, None)

            #first valid address will do
            if address_type == Address.PermanentAddress and valid_from <= arrow.now() and valid_until > arrow.now():
                return address

        return None
