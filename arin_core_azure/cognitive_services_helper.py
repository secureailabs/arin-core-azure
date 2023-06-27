from typing import List, Tuple

from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.cognitiveservices.models import Account
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.resource.subscriptions.models import Subscription


class CognitiveServicesHelper:
    def __init__(self):
        # Authenticate using default credentials
        self.credential = DefaultAzureCredential()

        # Initialize the subscription and compute management clients
        self.subscription_client = SubscriptionClient(self.credential)
        # Create a Cognitive Services Management client

    def subscription_list(self) -> List[Subscription]:
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

    def account_create(
        self, subscription_id: str, resource_group_name: str, account_name: str, location: str
    ) -> Account:
        # TODO we can look up the location from the resource group
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        print("Creating account...")
        account_creation = client.accounts.begin_create(resource_group_name, account_name, {"location": location})
        account_creation.wait()
        print("Done creating account...")
        return self.account_get(subscription_id, resource_group_name, account_name)

    def account_get(self, subscription_id: str, resource_group_name: str, account_name: str) -> Account:
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        return client.accounts.get(resource_group_name=resource_group_name, account_name=account_name)

    def account_get_endpoint(self, account: Account) -> str:
        return account.properties.endpoints["OpenAI Language Model Instance API"]  # type: ignore

    def account_get_api_key(self, account: Account) -> str:
        subscription_id, resource_group_name, account_name = self.account_get_locator_data(account)
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        return client.accounts.list_keys(resource_group_name, account_name).key1  # type: ignore # TODO no idea what key 2 does

    def account_get_engine_name(self, account: Account) -> str:
        subscription_id, resource_group_name, account_name = self.account_get_locator_data(account)
        client = CognitiveServicesManagementClient(self.credential, subscription_id)
        for deployment in client.deployments.list(resource_group_name, account_name):
            return deployment.name  # type: ignore
        raise Exception(f"No deployment found in account {account.id}")

    def account_get_locator_data(self, account: Account) -> Tuple[str, str, str]:
        id_part = str(account.id).split("/")
        subscription_id = id_part[2]
        resource_group_name = id_part[4]
        account_name = id_part[8]
        return subscription_id, resource_group_name, account_name

    def account_list(self) -> List[Account]:
        list_subscription = self.subscription_list()
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

    def account_list_for_kind(self, kind: str) -> List[Account]:
        list_account_selected = []
        list_account = self.account_list()
        for account in list_account:
            if account.kind == kind:
                list_account_selected.append(account)
            # print("Account name:", account.name)
            # print("Type:", account.type)
            # print("Kind:", account.kind)
            # print("SKU:", account.sku.name)
            # print("Location:", account.location)
            # print("Tags:", account.tags)
            # print("System data:", account.system_data)
            # print("Properties:", account.properties)
            # # print("Endpoint:", account.endpoint)
            # print()
        return list_account_selected
