from typing import List, Optional, Tuple

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Account
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.resource.subscriptions.models import Subscription

from arin_core_azure.base_helper import BaseHelper


class CognitiveServicesHelper(BaseHelper):
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        super().__init__(client_id, client_secret, tenant_id)

        # Initialize the subscription and compute management clients
        self.subscription_client = SubscriptionClient(self.credential)

        # Create a Cognitive Services Management client

    def list_subscription(self) -> List[Subscription]:
        # Get the subscription ID using the subscription name
        list_subscription = []
        for subscription in self.subscription_client.subscriptions.list():
            list_subscription.append(subscription)
        return list_subscription

    # def resource_create(self, subscription_id:str, resource_group_name: str, ) -> None:
    #     # Create a Resource Management client
    #     resource_client = ResourceManagementClient(self.credential, subscription_id)

    #     # Create a OpenAI Service Management client
    #     openai_client = OpenAIServiceClient(self.credential, subscription_id)

    #     # Define the location for the Azure OpenAI resource
    #     location = "westus"  # Specify your desired location

    #     # Create or update the resource group
    #     resource_client.resource_groups.create_or_update(resource_group_name, {"location": location})

    def create_account(
        self, subscription_id: str, resource_group_name: str, account_name: str, location: str
    ) -> Account:
        # TODO we can look up the location from the resource group
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        print("Creating account...")
        account_creation = client.accounts.begin_create(resource_group_name, account_name, {"location": location})
        account_creation.wait()
        print("Done creating account...")
        return self.get_account(subscription_id, resource_group_name, account_name)

    def get_account(self, subscription_id: str, resource_group_name: str, account_name: str) -> Account:
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        return client.accounts.get(resource_group_name=resource_group_name, account_name=account_name)

    def get_account_for_account_id(self, account_id: str) -> Account:
        subscription_id, resource_group_name, account_name = self.get_account_locator_data_for_account_id(account_id)
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        return client.accounts.get(resource_group_name=resource_group_name, account_name=account_name)

    def get_account_endpoint(self, account: Account) -> str:
        return account.properties.endpoints["OpenAI Language Model Instance API"]  # type: ignore

    def get_account_api_key(self, account: Account) -> str:
        subscription_id, resource_group_name, account_name = self.get_account_locator_data(account)
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        return client.accounts.list_keys(resource_group_name, account_name).key1  # type: ignore # TODO no idea what key 2 does

    def get_account_list_engine_name(self, account: Account) -> str:
        subscription_id, resource_group_name, account_name = self.get_account_locator_data(account)
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        list_engine_name = []
        for deployment in client.deployments.list(resource_group_name, account_name):
            list_engine_name.append(deployment.name)  # type: ignore
        return list_engine_name

    def get_account_locator_data(self, account: Account) -> Tuple[str, str, str]:
        id_part = str(account.id).split("/")
        subscription_id = id_part[2]
        resource_group_name = id_part[4]
        account_name = id_part[8]
        return subscription_id, resource_group_name, account_name

    def get_account_locator_data_for_account_id(self, account_id: str) -> Tuple[str, str, str]:
        id_part = account_id.split("/")
        subscription_id = id_part[2]
        resource_group_name = id_part[4]
        account_name = id_part[8]
        return subscription_id, resource_group_name, account_name

    def list_account(self) -> List[Account]:
        list_subscription = self.list_subscription()
        list_account = []
        for subscription in list_subscription:
            subscription_id = subscription.subscription_id
            if subscription_id is None:
                raise Exception("subscription_id is None")

            # Get the list of Cognitive Services accounts
            client = CognitiveServicesManagementClient(self.credential, subscription_id)

            for account in client.accounts.list():
                list_account.append(account)
        return list_account

    def list_account_name(self) -> List[str]:
        list_account_name = []
        for account in self.list_account():
            list_account_name.append(account.name)
        return list_account_name

    def list_account_for_kind(self, kind: str) -> List[Account]:
        list_account_selected = []
        list_account = self.list_account()
        for account in list_account:
            if account.kind == kind:
                list_account_selected.append(account)

        return list_account_selected
