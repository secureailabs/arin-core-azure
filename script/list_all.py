from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient

from arin_core_azure.resource_helper import ResourceHelper

# Authenticate using default credentials
helper = ResourceHelper()


# Get a list of subscriptions in your Azure account
subscriptions = helper.list_subscription()


# Iterate over each subscription
for subscription in subscriptions:

    helper.get_subscription_id(subscription.display_name)  # type: ignore
    print("---------------------------------------")
    print("---------------------------------------")
    print(f"Subscription: {subscription.display_name}")
    print(f" - ID: {subscription.subscription_id}")
    print(f" - State: {subscription.state}")
    print("---------------------------------------")
    # Set the subscription ID for the compute client
    compute_client = ComputeManagementClient(helper.credential, subscription_id=subscription.subscription_id)  # type: ignore

    # Get a list of resource groups in the subscription
    vms = compute_client.virtual_machines.list_all()
    # Iterate over each virtual machine
    for vm in vms:
        print(f"Subscription: {subscription.display_name}")
        print(f"Virtual Machine: {vm.name}")
        print(f" - ID: {vm.id}")
        print(f" - Location: {vm.location}")
        print(f" - VM Size: {vm.hardware_profile.vm_size}")  # type: ignore
        print(f" - OS Type: {vm.storage_profile.os_disk.os_type}")  # type: ignore
        print("---------------------------------------")
