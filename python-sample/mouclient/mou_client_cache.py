from datetime import datetime, timezone
from typing import Optional

from mouclient.api.service.iam_service import TokenResponse


class MouClientCache:
    def __init__(self) -> None:
        self.service_token_response: Optional[TokenResponse] = None

    @property
    def service_token(self) -> Optional[str]:
        return self.service_token_response.access_token if self.service_token_response is not None else None

    @property
    def has_valid_service_token(self) -> bool:
        return bool(
            self.service_token_response
            and self.service_token_response.expires_at
            and self.service_token_response.expires_at > datetime.now(timezone.utc)
        )
