from enum import Enum
import os

class Keys(Enum):
    MOU_SERVICE_ID = "MOU_SERVICE_ID"
    MOU_SERVICE_POD_NAME = "MOU_SERVICE_POD_NAME"
    MOU_SERVICE_CLIENT_ID = "MOU_SERVICE_CLIENT_ID"
    MOU_SERVICE_CLIENT_SECRET = "MOU_SERVICE_CLIENT_SECRET"
    MOU_IAM_REALM = "MOU_IAM_REALM"
    MOU_CONSENT_CLIENT_ID = "MOU_CONSENT_CLIENT_ID"
    MOU_CONSENT_CLIENT_SECRET = "MOU_CONSENT_CLIENT_SECRET"
    MOU_IAM_CONSENT_REALM = "MOU_IAM_CONSENT_REALM"
    MOU_IAM_SERVICE_URI = "MOU_IAM_SERVICE_URI"
    MOU_POD_SERVICE_URI = "MOU_POD_SERVICE_URI"
    MOU_NOTIFICATION_SERVICE_URI = "MOU_NOTIFICATION_SERVICE_URI"
    MOU_DECRYPT_SERVICE_URI = "MOU_DECRYPT_SERVICE_URI"
    MOU_VC_SERVICE_URI = "MOU_VC_SERVICE_URI"
    MOU_COMMON_CONTEXT_URI = "MOU_COMMON_CONTEXT_URI"
    MOU_DISABLE_SSL_VERIFICATION = "MOU_DISABLE_SSL_VERIFICATION"
    GLOBAL_TIMEOUT = "GLOBAL_TIMEOUT"


class ServiceConfiguration:

    iam_service_uri = None
    pod_service_uri = None
    notification_service_uri = None
    decrypt_service_uri = None
    vc_service_uri = None
    mou_common_context_uri = None
    client_id = None
    client_secret = None
    consent_client_id = None
    consent_client_secret = None
    service_id = None
    pod_name = None
    iam_realm = None
    iam_consent_realm = None
    service_profile_uri = None
    service_consents_uri = None

    global_timeout = 10
    verify_ssl = True

    @classmethod
    def init(cls) -> None:
        cls.iam_service_uri = os.getenv(Keys.MOU_IAM_SERVICE_URI.value)
        cls.pod_service_uri = os.getenv(Keys.MOU_POD_SERVICE_URI.value)
        cls.notification_service_uri = os.getenv(Keys.MOU_NOTIFICATION_SERVICE_URI.value)
        cls.decrypt_service_uri = os.getenv(Keys.MOU_DECRYPT_SERVICE_URI.value)
        cls.vc_service_uri = os.getenv(Keys.MOU_VC_SERVICE_URI.value)
        cls.mou_common_context_uri = os.getenv(Keys.MOU_COMMON_CONTEXT_URI.value)
        cls.client_id = os.getenv(Keys.MOU_SERVICE_CLIENT_ID.value)
        cls.client_secret = os.getenv(Keys.MOU_SERVICE_CLIENT_SECRET.value)
        cls.consent_client_id = os.getenv(Keys.MOU_CONSENT_CLIENT_ID.value)
        cls.consent_client_secret = os.getenv(Keys.MOU_CONSENT_CLIENT_SECRET.value)
        cls.service_id = os.getenv(Keys.MOU_SERVICE_ID.value)
        cls.pod_name = os.getenv(Keys.MOU_SERVICE_POD_NAME.value)

        cls.iam_realm = os.getenv(Keys.MOU_IAM_REALM.value)
        cls.iam_consent_realm = os.getenv(Keys.MOU_IAM_CONSENT_REALM.value)
        cls.service_profile_uri = f"{cls.pod_service_uri}{cls.pod_name}/profile/card#me"
        cls.service_consents_uri = f"{cls.pod_service_uri}{cls.pod_name}/consents/"
        cls.global_timeout = int( os.getenv(Keys.GLOBAL_TIMEOUT.value, "10") )
        cls.verify_ssl = False if os.getenv(Keys.MOU_DISABLE_SSL_VERIFICATION.value) == "true" else True
