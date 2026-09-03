import mouclient.const
from datetime import datetime

from typing import List
from httpx import Response
from mouclient.api.service.mou_base_service import MouBaseService
from mouclient.api.service.service_configuration import ServiceConfiguration
from mouclient.serializable import SerializableEnum, SerializableObject, UriRefEnum
from mouclient.utils import parse_datetime
from mouclient.namespace import GCONSENT, W3_ACL, MOUVC

class Mode(SerializableEnum):
    READ = W3_ACL.Read
    WRITE = W3_ACL.Write
    APPEND = W3_ACL.Append

class ConsentStatus(SerializableEnum):
    REQUESTED = GCONSENT.ConsentStatusRequested
    EXPLICITLY_GIVEN = GCONSENT.ConsentStatusExplicitlyGiven

class UsageLimit(UriRefEnum):
    ONE_TIME = MOUVC.UsageLimitOneTime
    AFTER_CHANGE = MOUVC.UsageLimitAfterChange
    DAILY = MOUVC.UsageLimitPeriodicDaily
    WEEKLY = MOUVC.UsageLimitPeriodicWeekly
    MONTHLY = MOUVC.UsageLimitPeriodicMonthly
    YEARLY = MOUVC.UsageLimitPeriodicYearly

    @classmethod
    def _namespace(cls) -> str:
        return str(MOUVC)

    @classmethod
    def _prefixes(cls) -> List[str]:
        return ["mouvc"]

    # FIXME only temporary while backend verify service onyl accepts form of mouvc:...
    @classmethod
    def _serialize_with_prefix(cls) -> bool:
        return True

class AccessGrant(SerializableObject):
    def __init__(self,
        mode: List[str],
        forPersonalData: List[str],
        isProvidedTo: List[str],
        hasStatus: ConsentStatus = ConsentStatus.EXPLICITLY_GIVEN,
        forPurpose: List[str] = None,
        serviceId: str = None,
        usageLimit: UsageLimit = UsageLimit.ONE_TIME
    ) -> None:
        super().__init__()
        self.mode = list(map(lambda m: Mode.create(m), mode))
        self.forPersonalData = forPersonalData
        self.isProvidedTo = isProvidedTo
        self.hasStatus = ConsentStatus.create(hasStatus)
        self.forPurpose = forPurpose
        self.serviceId = serviceId
        self.usageLimit = UsageLimit.create(usageLimit)


class AccessRequest(SerializableObject):
    def __init__(self,
        mode: List[Mode],
        isConsentForDataSubject: List[str],
        forPersonalData: List[str],
        hasStatus: ConsentStatus = ConsentStatus.REQUESTED,
        forPurpose: List[str] = None,
        serviceId: str = None,
        usageLimit: UsageLimit = UsageLimit.ONE_TIME
    ) -> None:
        super().__init__()
        self.mode = mode
        self.hasStatus = ConsentStatus.create(hasStatus)
        self.isConsentForDataSubject = isConsentForDataSubject
        self.forPersonalData = forPersonalData
        self.forPurpose = forPurpose
        self.serviceId = serviceId
        self.usageLimit = usageLimit

class ServiceLinkRecord(SerializableObject):
    def __init__(self,
        version: str,
        iat: datetime,
        linkId: str,
        operatorId: str,
        serviceId: str,
        surrogateId: str,
        serviceDescriptionVersion: str = None
    ) -> None:
        super().__init__()
        self.version = version
        self.iat = parse_datetime(iat)
        self.linkId = linkId
        self.operatorId = operatorId
        self.serviceId = serviceId
        self.surrogateId = surrogateId
        self.serviceDescriptionVersion = serviceDescriptionVersion

class Issuer(SerializableObject):
    def __init__(self, id: str) -> None:
        super().__init__()
        self.id = id

class Proof(SerializableObject):
    def __init__(self, created: datetime, type: str, proofPurpose: str, verificationMethod: str, domain: str = None, proofValue: str = None, jws: str = None) -> None:
        super().__init__()
        self.created = parse_datetime(created)
        self.domain = domain
        self.type = type
        self.proofPurpose = proofPurpose
        self.proofValue = proofValue
        self.jws = jws
        self.verificationMethod = verificationMethod


class CredentialSubject(SerializableObject):
    def __init__(self, inbox: str = None, hasConsent: AccessRequest = None, providedConsent: AccessGrant = None, serviceLinkRecord: ServiceLinkRecord = None) -> None:
        super().__init__()
        self.inbox = inbox
        self.hasConsent = AccessRequest.create(hasConsent)
        self.providedConsent = AccessGrant.create(providedConsent)
        self.serviceLinkRecord = ServiceLinkRecord.create(serviceLinkRecord)

class VerifiableCredentialSubject(CredentialSubject):
    def __init__(self, id: str, inbox: str = None, hasConsent: AccessRequest = None, providedConsent: AccessGrant = None, serviceLinkRecord: ServiceLinkRecord = None) -> None:
        super().__init__(inbox, hasConsent, providedConsent, serviceLinkRecord)
        self.id = id

class CredentialStatus(SerializableObject):
    def __init__(self, id: str, revocationListCredential: str, revocationListIndex: str, type: str) -> None:
        super().__init__()
        self.id = id
        self.revocationListCredential = revocationListCredential
        self.revocationListIndex = revocationListIndex
        self.type = type # RevocationList2020Status

class CredentialStatusPayload(SerializableObject):
    def __init__(self, status: str, type: str = mouclient.const.CREDENTIAL_STATUS_REVOCATION_LIST_2020) -> None:
        super().__init__()
        self.status = status # "0" | "1"
        self.type = type

class CredentialUsageLimit(SerializableObject):
    def __init__(self, id: str, type: str, usageListIndex: str) -> None:
        super().__init__()
        self.id = id
        self.type = type
        self.usageListIndex = usageListIndex

class Credential(SerializableObject):
    props_to_json_keys = {"context": "@context"}

    def __init__(self, context: List[str], credentialSubject: CredentialSubject, issuanceDate: datetime = None, expirationDate: datetime = None) -> None:
        super().__init__()
        self.context = context
        self.credentialSubject = CredentialSubject.create(credentialSubject)
        self.issuanceDate = parse_datetime(issuanceDate)
        self.expirationDate = parse_datetime(expirationDate)



class VerifiableCredential(Credential):
    def __init__(self,
        context: List[str],
        credentialStatus: CredentialStatus,
        credentialSubject: VerifiableCredentialSubject,
        id: str,
        issuer: Issuer,
        proof: Proof,
        type: List[str],
        issuanceDate: datetime = None,
        expirationDate: datetime = None,
        credentialUsageLimit: CredentialUsageLimit = None
    ) -> None:
        credentialSubject = VerifiableCredentialSubject.create(credentialSubject)
        super().__init__(context, credentialSubject, issuanceDate, expirationDate)
        self.credentialStatus = CredentialStatus.create(credentialStatus)
        self.id = id
        self.issuer = Issuer.create(issuer)
        self.proof = Proof.create(proof)
        self.type = type
        self.credentialUsageLimit = CredentialUsageLimit.create(credentialUsageLimit)

class IssueRequest(SerializableObject):
    def __init__(self, credential: Credential) -> None:
        super().__init__()
        self.credential = Credential.create(credential)

class StatusRequest(SerializableObject):
    def __init__(self, credentialId: str, credentialStatus: List[CredentialStatusPayload]) -> None:
        super().__init__()
        self.credentialId = credentialId
        self.credentialStatus = []
        for payload in credentialStatus:
            p = CredentialStatusPayload.create(payload)
            self.credentialStatus.append(p)

class VerifyRequest(SerializableObject):
    def __init__(self, vc: VerifiableCredential) -> None:
        super().__init__()
        self.verifiableCredential = vc

class VerifyResponse(SerializableObject):
    def __init__(self, checks: List[str], warnings: List[str], errors: List[str]) -> None:
        super().__init__()
        self.checks = checks
        self.warnings = warnings
        self.errors = errors

    @property
    def is_ok(self) -> bool:
        return len(self.errors) == 0

class VCService(MouBaseService):

    def _base_url(self) -> str:
        return ServiceConfiguration.vc_service_uri

    async def issue(self, issue_request: IssueRequest, auth: str) -> VerifiableCredential:
        headers = {"Authorization": auth}
        raw_response = await self._post_raw_json("/issue", body=issue_request, headers=headers)
        self._raise_for_status(raw_response)
        return VerifiableCredential.create(raw_response.json())

    async def verify(self, vc: VerifiableCredential) -> VerifyResponse:
        raw_response = await self._post_raw_json("/verify", body=VerifyRequest(vc), headers={})
        self._raise_for_status(raw_response)
        return VerifyResponse.create(raw_response.json())

    async def status(self, status_request: StatusRequest, auth: str) -> Response:
        headers = {"Authorization": auth}
        raw_response = await self._post_raw_json("/status", body=status_request, headers=headers)
        self._raise_for_status(raw_response)
        return raw_response
