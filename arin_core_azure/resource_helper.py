from typing import List, Optional

from azure.mgmt.resource.resources import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.resource.subscriptions.models import Subscription

from arin_core_azure.base_helper import BaseHelper


class ResourceHelper(BaseHelper):
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        super().__init__(client_id, client_secret, tenant_id)
        # Initialize the subscription client
        self.subscription_client = SubscriptionClient(self.credential)

    def list_subscription(self) -> List[Subscription]:
        # Get the subscription ID using the subscription name
        list_subscription = []
        for subscription in self.subscription_client.subscriptions.list():
            list_subscription.append(subscription)
        return list_subscription

    def list_subscription_id(self) -> List[str]:
        # Get the subscription ID using the subscription name
        list_subscription_id = []
        for subscription in self.subscription_client.subscriptions.list():
            list_subscription_id.append(subscription.subscription_id)
        return list_subscription_id

    def list_subscription_name(self) -> List[str]:
        # Get the subscription ID using the subscription name
        list_subscription_name = []
        for subscription in self.subscription_client.subscriptions.list():
            list_subscription_name.append(subscription.display_name)
        return list_subscription_name

    def get_subscription_by_id(self, subscription_id: str) -> Subscription:
        # Get the subscription using the subscription name
        subscription = self.subscription_client.subscriptions.get(subscription_id=subscription_id)
        if subscription is None:
            raise ValueError(f"Subscription with id {subscription_id} not found")
        return subscription  # type: ignore

    def get_subscription_by_name(self, subscription_name: str) -> Subscription:
        # Get the subscription using the subscription name
        for subscription in self.subscription_client.subscriptions.list():
            if subscription.display_name == subscription_name:
                return subscription  # type: ignore

        raise ValueError(f"Subscription with name {subscription_name} not found")

    def get_subscription_id(self, subscription_name: str) -> str:
        # Get the subscription ID using the subscription name
        subscription = self.get_subscription_by_name(subscription_name)
        if subscription.subscription_id is None:
            raise ValueError(f"Subscription_id with name {subscription_name} not found, this is really weird")
        return subscription.subscription_id

    def list_resource_group_all(self, subscription_id: str) -> List[ResourceGroup]:
        list_resource_group = []
        for subscription in self.subscription_client.subscriptions.list():
            # Initialize the ResourceManagementClient
            resource_management_client = ResourceManagementClient(self.credential, subscription_id=subscription_id)

            # Get the list of resource groups
            for subscription in resource_management_client.resource_groups.list():
                list_resource_group.append(subscription)
        return list_resource_group

    def delete_resource_group(self, subscription_id: str, resource_group_name: str, verbose: Optional[bool] = True):

        resource_management_client = ResourceManagementClient(self.credential, subscription_id=subscription_id)
        if verbose:
            print(f"Deleting resource group {resource_group_name}...")
        resource_management_client.resource_groups.begin_delete(resource_group_name).wait()
        if verbose:
            print(f"Deleted resource group {resource_group_name}.")
