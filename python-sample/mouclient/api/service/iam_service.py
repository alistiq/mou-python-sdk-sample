from datetime import datetime, timedelta, timezone

from mouclient.api.service.mou_base_service import MouBaseService
from mouclient.api.service.service_configuration import ServiceConfiguration
from mouclient.serializable import SerializableObject

class TokenResponse(SerializableObject):
    props_to_json_keys = {"not_before_policy": "not-before-policy"}
    props_to_ignore = ["expires_at"]

    def __init__(
        self,
        access_token: str,
        expires_in: int,
        refresh_expires_in: int,
        token_type: str,
        not_before_policy: int,
        scope: str,
        refresh_token: str = None,
        id_token: str = None
    ) -> None:
        super().__init__()
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.refresh_expires_in = refresh_expires_in
        self.token_type = token_type
        self.not_before_policy = not_before_policy
        self.scope = scope
        self.id_token = id_token

        # not part of the original json, helper property
        if self.expires_in:
            self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.expires_in)


class IAMService(MouBaseService):

    def _base_url(self) -> str:
        return ServiceConfiguration.iam_service_uri

    async def fetch_service_access_token(self, grant_type: str, client_id: str, client_secret: str) -> TokenResponse:
        data = {"grant_type": grant_type, "client_id": client_id, "client_secret": client_secret}
        path = f"realms/{ServiceConfiguration.iam_realm}/protocol/openid-connect/token"
        return await self._post_token(path, data)

    async def fetch_consent_access_token(self, grant_type: str, client_id: str, client_secret: str, consent_grant: bytes = None) -> TokenResponse:
        data = {"grant_type": grant_type, "client_id": client_id, "client_secret": client_secret}
        if consent_grant is not None:
            data["consent_grant"] = consent_grant.decode("ascii")
        path = f"realms/{ServiceConfiguration.iam_consent_realm}/protocol/openid-connect/token"
        return await self._post_token(path, data)

    async def _post_token(self, path: str, data: dict) -> TokenResponse:
        raw_response = await self._client.post(path, data=data)
        self._raise_for_status(raw_response)
        return TokenResponse.from_dictionary(raw_response.json())
