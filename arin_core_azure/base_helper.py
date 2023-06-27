from typing import Optional

from azure.identity import ClientSecretCredential, DefaultAzureCredential


class BaseHelper:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ):
        if client_id is None and client_secret is None and tenant_id is None:
            # Authenticate using default credentials
            self.credential = DefaultAzureCredential()
        elif client_id is not None and client_secret is not None and tenant_id is not None:
            # Authenticate using client_id and client_secret and tenant_id
            self.credential = ClientSecretCredential(
                client_id=client_id, client_secret=client_secret, tenant_id=tenant_id
            )
        else:
            raise ValueError("Either all or none of the parameters should be specified")
