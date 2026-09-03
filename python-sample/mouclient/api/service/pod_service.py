from typing import Any, Optional
from mouclient.api.service.mou_base_service import MouBaseService
from mouclient.api.service.service_configuration import ServiceConfiguration

class PodService(MouBaseService):

    def _base_url(self) -> str:
        return ServiceConfiguration.pod_service_uri

    async def get_container_resource(self, resource_path: str, auth: str) -> str:
        headers = {"Authorization": auth, "Accept": "application/json"}
        raw_response = await self._client.get(resource_path, headers=headers)
        self._raise_for_status(raw_response)
        return raw_response.text

    async def post_container_resource(self, resource_path: str, auth: str, body: Optional[Any] = None) -> str:
        headers = {"Authorization": auth}
        raw_response = await self._post_raw_json(resource_path, body=body, headers=headers)
        self._raise_for_status(raw_response)
        return raw_response.text

    async def get_last_consent(self, web_id: str, auth: str) -> str:
        # NOTE: sending an "Accept: application/json" header here causes a timeout
        # when the holder has no consent yet, so it is intentionally omitted.
        headers = {"Authorization": auth}
        resource_path = f"{ServiceConfiguration.service_consents_uri}last"
        # service is taking a bit longer to respond, we need to increase timeouts
        raw_response = await self._client.get(resource_path, headers=headers, params={"webid": web_id}, timeout=20)
        self._raise_for_status(raw_response)
        return raw_response.text

    async def get_consents(self, auth: str, web_id: str = None) -> str:
        headers = {"Authorization": auth}
        params = {"webid": web_id} if web_id is not None else {}
        raw_response = await self._client.get(ServiceConfiguration.service_consents_uri, headers=headers, params=params, timeout=20)
        self._raise_for_status(raw_response)
        return raw_response.text
