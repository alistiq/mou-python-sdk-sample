from mouclient.api.service.mou_base_service import MouBaseService
from mouclient.api.service.service_configuration import ServiceConfiguration
from mouclient.serializable import SerializableObject

class DecryptInput(SerializableObject):

    def __init__(self, jwe: str, walletPassword: str = None) -> None:
        super().__init__()
        self.jwe = jwe
        self.walletPassword = walletPassword

class DecryptService(MouBaseService):

    def _base_url(self) -> str:
        return ServiceConfiguration.decrypt_service_uri

    async def decrypt(self, decrypt_input: DecryptInput, auth: str) -> str:
        headers = {"Authorization": auth}
        resp = await self._post_raw_json(path="/decrypt", body=decrypt_input, headers=headers)
        self._raise_for_status(resp)
        return resp.text
