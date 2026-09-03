import jsonpickle

from typing import Any, Optional
from httpx import AsyncClient, Response
from mouclient.api.service.exceptions import ErrorBody, MouApiError
from mouclient.api.service.service_configuration import ServiceConfiguration

class MouBaseService:

    def __init__(self) -> None:
        self._client = AsyncClient(base_url=self._base_url(), timeout=self._timeout(), verify=self._verify_ssl())

    def _base_url(self) -> str:
        raise NotImplementedError("Subclasses of MouBaseService must implement _base_url() method and return base url of the service.")

    def _timeout(self) -> int:
        return ServiceConfiguration.global_timeout

    def _verify_ssl(self) -> bool:
        return ServiceConfiguration.verify_ssl

    async def close(self):
        await self._client.aclose()

    async def _post_raw_json(self, path: str, body: Any, headers: Optional[dict] = None) -> Response:
        # we need to use custom json serialization, so calling httpx.post with 'json' parameter won't work
        headers = dict(headers) if headers else {}
        headers["Content-Type"] = "application/json"
        content = jsonpickle.encode(body, unpicklable=False)
        return await self._client.post(path, headers=headers, content=content)

    def _raise_for_status(self, response: Response) -> None:
        if response.status_code < 400:
            return None
        if response.text is not None:
            try:
                error_body = ErrorBody.create(response.json())
            except Exception:
                error_body = ErrorBody(response.text)

            raise MouApiError(response.status_code, error_body)
        response.raise_for_status()
