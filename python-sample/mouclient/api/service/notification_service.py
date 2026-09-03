from datetime import datetime, timezone
from typing import Optional
from httpx import Response
from mouclient.api.service.mou_base_service import MouBaseService
from mouclient.api.service.service_configuration import ServiceConfiguration
from mouclient.api.service.vc_service import VerifiableCredential
from mouclient.serializable import SerializableEnum, SerializableObject
from mouclient.utils import parse_datetime

class MessageType(SerializableEnum):
    ACCESS_REQUEST = "moucmn:NotificationAccessRequest"


class MessagePayload(SerializableObject):
    props_to_json_keys = {"type": "@type"}

    def __init__(
        self,
        subject: str,
        message: str,
        type: str = "MessagePayload",
        id: str = None,
        createdDate: Optional[datetime] = None,
        transactionID:str = None,
        dataSet:str = None,
        accessRequest:VerifiableCredential = None,
        url:str = "https://csru.sk/more_information"
    ) -> None:
        super().__init__()
        self.subject = subject
        self.message = message
        self.type = type
        self.id = id
        self.createdDate = createdDate if createdDate is not None else datetime.now(timezone.utc)
        self.transactionID = transactionID
        self.dataSet = dataSet
        self.accessRequest = VerifiableCredential.create(accessRequest)
        self.url = url


class Message(SerializableObject):
    props_to_json_keys = {"context": "@context", "type": "@type"}

    def __init__(self, context: str, source: str, person: str, messageType: MessageType, payload: MessagePayload, type: str = "Message", observedDate: Optional[datetime] = None) -> None:
        super().__init__()
        self.context = context
        self.source = source
        self.person = person
        self.messageType = MessageType.create(messageType)
        self.payload = MessagePayload.create(payload)
        self.type = type
        self.observedDate = parse_datetime(observedDate) if observedDate is not None else datetime.now(timezone.utc)

class NotificationService(MouBaseService):

    def _base_url(self) -> str:
        return ServiceConfiguration.notification_service_uri

    async def notification(self, message: Message, auth: str) -> Response:
        headers = {"Authorization": auth}
        raw_resp = await self._post_raw_json("/notification", body=message, headers=headers)
        self._raise_for_status(raw_resp)
        return raw_resp
