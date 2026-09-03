import asyncio
import base64
import typing

from functools import wraps
from httpx import codes
from typing import Any, List, Optional
from types import TracebackType
from rdflib import Graph, URIRef

import mouclient.const
from mouclient.api.service.decrypt_service import DecryptInput, DecryptService
from mouclient.api.service.exceptions import MouApiError
from mouclient.api.service.iam_service import IAMService, TokenResponse
from mouclient.api.service.pod_service import PodService
from mouclient.api.service.notification_service import Message, MessagePayload, MessageType, NotificationService
from mouclient.api.service.vc_service import (
    AccessRequest,
    Credential,
    CredentialSubject,
    IssueRequest,
    Mode,
    UsageLimit,
    VCService,
    VerifiableCredential,
)
from mouclient.utils import bearer_auth, dpop_auth, pod_to_web_id, web_id_to_pod
from mouclient.mou_client_cache import MouClientCache
from mouclient.api.service.service_configuration import ServiceConfiguration
from mouclient.namespace import GCONSENT, W3_CREDENTIALS, W3_ACL, MOUVC

U = typing.TypeVar("U", bound="MouClient")

def ensure_service_login(func):
    @wraps(func)
    async def func_wrapper(*args, **kwargs):
        """Decorator that ensures we have a valid servis token.
        Performs service login if neccessary.
        Works with async methods of MouClient only!
        """
        if isinstance(args[0], MouClient):
            client = args[0]
            if not client.cache.has_valid_service_token:
                await client.service_log_in()
        return await func(*args, **kwargs)
    return func_wrapper

class MouClient:

    def __init__(self) -> None:
        # we need to delay service configuration creation until
        # the app has a chance to populate environment variables
        # but before relying services are created
        ServiceConfiguration.init()
        self.cache = MouClientCache()
        self.iam_service = IAMService()
        self.pod_service = PodService()
        self.vc_service = VCService()
        self.notification_service = NotificationService()
        self.decrypt_service = DecryptService()

    async def close(self):
        """
        Unlike the sync case, we cannot silently close the client when
        it is garbage collected, because `.close()` is an async operation,
        but `__del__` is not.
        """
        await self.iam_service.close()
        await self.pod_service.close()
        await self.vc_service.close()
        await self.notification_service.close()
        await self.decrypt_service.close()

    # context management
    async def __aenter__(self: U) -> U:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[typing.Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        await self.close()

    async def service_log_in(self) -> TokenResponse:
        resp = await self.iam_service.fetch_service_access_token(
            "client_credentials",
            ServiceConfiguration.client_id,
            ServiceConfiguration.client_secret
        )
        # in case of successful response, cache the token
        self.cache.service_token_response = resp
        return resp

    async def perform_consent_token_request(self, access_grant:str) -> TokenResponse:
        base64_encoded_grant = base64.urlsafe_b64encode(access_grant.encode('ascii'))
        resp = await self.iam_service.fetch_consent_access_token(
            "client_credentials",
            ServiceConfiguration.consent_client_id,
            ServiceConfiguration.consent_client_secret,
            base64_encoded_grant
        )
        return resp

    @ensure_service_login
    async def issue_access_request_vc(
        self,
        resource_uris:List[str],
        modes:List[Mode],
        usageLimit: UsageLimit = UsageLimit.ONE_TIME
    ) -> VerifiableCredential:

        resources = list(map(self._pod_absolute_uris, resource_uris))
        request = IssueRequest(
            credential=Credential(
                context=[
                    mouclient.const.W3_ORG_CREDENTIALS_CONTEXT,
                    str(MOUVC)
                ],
                credentialSubject=CredentialSubject(
                    inbox=ServiceConfiguration.service_consents_uri,
                    hasConsent=AccessRequest(
                        mode=modes,
                        isConsentForDataSubject=ServiceConfiguration.service_profile_uri,
                        forPersonalData=resources,
                        serviceId=ServiceConfiguration.service_id,
                        usageLimit=usageLimit
                    )
                )
            )
        )
        vc = await self.vc_service.issue(
            issue_request=request,
            auth=bearer_auth(self.cache.service_token)
        )
        return vc

    @ensure_service_login
    async def send_access_request_notification(
        self,
        web_id:str,
        access_request:VerifiableCredential,
        subject:str,
        message:str = None
    ):

        message = Message(
            context=ServiceConfiguration.mou_common_context_uri,
            source=ServiceConfiguration.service_profile_uri,
            person=web_id_to_pod(web_id),
            messageType=MessageType.ACCESS_REQUEST,
            payload=MessagePayload(
                subject=subject,
                message=message,
                accessRequest=access_request
            )
        )
        await self.notification_service.notification(message=message, auth=bearer_auth(self.cache.service_token))
        # the service is not returning any body, so either it raises an exception because of bad response status
        # or if 200 OK, then nothing is returned

    @ensure_service_login
    async def get_valid_dataset_access_grant(
        self,
        holder_username: str,
        resource_names: List[str],
        modes: List[Mode] = None, # do not check by default
        usageLimit: UsageLimit = None # do not check by default
    ) -> Optional[str]:
        """Looks for consent grant for the holder, for the specified resources, validates it
        and returns.
        If the grant does not exist or was revoked, returns None.
        Resource names must be only a simple names of resources under holders POD dataset container (used for MOU)
        """

        holder_web_id = pod_to_web_id(holder_username, ServiceConfiguration.pod_service_uri)
        #handle correctly 404 NotFound
        try:
            latest_grant = await self.get_last_access_grant_from(granter_web_id=holder_web_id)
        except MouApiError as api_error:
            if api_error.status_code == codes.NOT_FOUND:
                print(f"No grant for holder {holder_username}!")
                return None
            else:
                raise api_error

        # check required resources
        resources = self._dataset_absolute_uris(holder_username, resource_names)
        if not self._check_grant_is_for_resources(
            grant=latest_grant,
            web_id=holder_web_id,
            resources=resources,
            modes=modes,
            usageLimit=usageLimit
        ):
            print(f"Latest grant is not for all required resources ({resources}), it can't be used")
            return None

        # check validity, revocation is not needed
        # last access grant API already checks that..

        return latest_grant


    @ensure_service_login
    async def request_dataset_access(
        self,
        holder_username: str,
        resource_names: List[str],
        notification_subject: str,
        notification_message: str = None,
        modes: Optional[List[Mode]] = None,
        usageLimit:UsageLimit = UsageLimit.ONE_TIME
    ):
        """Higher level API to perform steps to request access to resources
        1. service log in if neccessary
        2. issue access request VC
        3. send access request notification to holder
        For step 3 a human readable subject(title) and message displayed to the user is needed.
        Resource names must be only a simple names of resources under holders POD dataset container (used for MOU)
        """
        modes = modes if modes is not None else [Mode.READ]
        resource_rel_uris = list(map(lambda name: self._dataset_rel_uri(holder_username, name), resource_names))
        access_request = await self.issue_access_request_vc(resource_rel_uris, modes, usageLimit)
        web_id = pod_to_web_id(holder_username, ServiceConfiguration.pod_service_uri)
        await self.send_access_request_notification(
            web_id=web_id,
            access_request=access_request,
            subject=notification_subject,
            message=notification_message
        )

    @ensure_service_login
    async def await_dataset_access(
        self,
        holder_username: str,
        resource_names: List[str],
        modes: Optional[List[Mode]] = None,
        max_retries: int = 10,
        retry_wait_time: int = 10
    ) -> Optional[str]:
        modes = modes if modes is not None else [Mode.READ]
        retry_num = 0
        while retry_num < max_retries:

            latest_grant = await self.get_valid_dataset_access_grant(holder_username=holder_username, resource_names=resource_names, modes=modes)

            if latest_grant:
                print("GOT grant for resources..")
                return latest_grant
            elif retry_num < max_retries:
                print(f"Attempt #{retry_num+1} NOT correct grant, will wait {retry_wait_time} seconds..")
                retry_num+=1
                await asyncio.sleep(retry_wait_time)
        print(f"No new grant for required resources after {max_retries} attempts, aborting..")
        return None

    async def post_pod_container_resource(self, resource_path: str, token: str, body: Optional[Any] = None) -> str:
        """General POST method, resource path must be Solid server relative path starting with POD name
        e.g. martinspod/dataset-container/my-personal-resource and the token must grant WRITE access
        to that POD and that resource/container. Cannot be used for creating containers.
        """
        return await self.pod_service.post_container_resource(
            resource_path=resource_path,
            auth=bearer_auth(token),
            body=body
        )

    async def get_pod_container_resource(self, resource_path: str, token: str) -> str:
        """General GET method, resource path must be Solid server relative path starting with POD name
        e.g. martinspod/dataset-container/my-personal-resource and the token must grant READ access
        to that POD and that resource. Cannot be used to list containers content.
        """
        return await self.pod_service.get_container_resource(
            resource_path=resource_path,
            auth=bearer_auth(token)
        )

    async def get_dataset_resource(self, pod: str, resource: str, token: str) -> str:
        """Convenient method to GET resources from dataset container specific for MOU.
        The token must grand READ access to the POD and that resource."""
        rel_uri = self._dataset_rel_uri(pod, resource)
        return await self.get_pod_container_resource(rel_uri, token)

    @ensure_service_login
    async def get_access_grants_from(self, granter_web_id: str) -> str:
        return await self.pod_service.get_consents(bearer_auth(self.cache.service_token), granter_web_id)

    @ensure_service_login
    async def get_last_access_grant_from(self, granter_web_id: str) -> str:
        return await self.pod_service.get_last_consent(granter_web_id, bearer_auth(self.cache.service_token))

    async def verify_access_grant(self, access_grant: str) -> bool:
        try:
            vc = VerifiableCredential.create(access_grant)
        except Exception:
            print("Error deserializing access grant from service's POD into VC object.")
            return False

        try:
            resp = await self.vc_service.verify(vc)
        except MouApiError as e:
            print(f"API error in Verify VC : {e}")
            return False

        return resp.is_ok


    @ensure_service_login
    async def decrypt_resource(self, jwe: str, walletPassword: str = "") -> str:
        input = DecryptInput(
            jwe=jwe,
            walletPassword=walletPassword
        )
        resp = await self.decrypt_service.decrypt(input, dpop_auth(self.cache.service_token))
        return resp

    def _pod_absolute_uris(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{ServiceConfiguration.pod_service_uri}{path}"

    def _dataset_rel_uri(self, holder: str, resource: str) -> str:
        return f"{holder}/dataset/{resource}"

    def _dataset_absolute_uris(self, holder: str, resource_names: List[str]) -> List[str]:
        resource_rel_uris = list(map(lambda name: self._dataset_rel_uri(holder, name), resource_names))
        return list(map(self._pod_absolute_uris, resource_rel_uris))

    def _check_grant_is_for_resources(
        self, grant: str,
        web_id: str,
        resources: List[str],
        modes: List[Mode] = None,
        usageLimit: UsageLimit = None
    ) -> bool:
        graph = Graph()
        graph.parse(data=grant, format="json-ld")

        web_id_uri = URIRef(web_id)
        # first check if this grant is for requested web_id
        try:
            cred_id = graph.value(predicate=W3_CREDENTIALS.credentialSubject, object=web_id_uri, any=False)
        except Exception:
            return False

        if cred_id is None:
            return False

        # then grab the BNode for provided consent
        try:
            provided_consent = graph.value(subject=web_id_uri, predicate=GCONSENT.providedConsent, any=False)
        except Exception:
            return False
        if provided_consent is None:
            return False


        # now go through all resources and check presence in forPersonalData
        for res in resources:
            res_uri = URIRef(res)
            if not (provided_consent, GCONSENT.forPersonalData, res_uri) in graph:
                return False

        # check also modes if passed as argument
        if modes:
            for mode in modes:
                if not (provided_consent, W3_ACL.mode, mode.value) in graph:
                    return False

        # check usage limit if passed in
        if usageLimit:
            if not (provided_consent, MOUVC.usageLimit, usageLimit.value) in graph:
                return False

        # all checks OK
        return True
