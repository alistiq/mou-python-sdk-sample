import os
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class MOUVC(DefinedNamespace):

    # http://www.w3.org/1999/02/22-rdf-syntax-ns#Property
    serviceId: URIRef
    usageLimit: URIRef
    credentialUsageLimit: URIRef

    # http://www.w3.org/2000/01/rdf-schema#Class
    UsageLimitType: URIRef

    UsageLimitOneTime: URIRef
    UsageLimitAfterChange: URIRef
    UsageLimitPeriodicDaily: URIRef
    UsageLimitPeriodicWeekly: URIRef
    UsageLimitPeriodicMonthly: URIRef
    UsageLimitPeriodicYearly: URIRef

    UsageLimitList2022Status: URIRef



    # the actual namespace is dependant on service configuration
    # URL is changing based on deployment environment
    # namespace URL gets updated upon start and load of env vars
    _NS = Namespace(f"{os.getenv('MOU_VC_SERVICE_URI', 'https://your-mou-host.example.com:4443/')}credentials/v1/")
