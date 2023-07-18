from arin_core_azure.blob_helper import BlobHelper
from arin_core_azure.resource_helper import ResourceHelper


def print_storage(print_blob: bool = False):
    resource_helper = ResourceHelper()
    subscription_list = resource_helper.list_subscription()
    for subscription in subscription_list:
        print(f"Subscription: {subscription.display_name}")
        helper = BlobHelper()
        list_account = helper.list_account(subscription_id=subscription.subscription_id)
        for account in list_account:
            print(f"  Storage account: {account.name}")
            list_container = helper.list_container_name(account.name)
            for container in list_container:
                print(f"    Container: {container}")
                if print_blob:
                    try:
                        list_blob_name = helper.list_blob_name(account.name, container)
                        for blob_name in list_blob_name:
                            blob_client = helper.get_blob_client(
                                storage_account_name=account.name, container_name=container, blob_name=blob_name
                            )
                            blob_properties = blob_client.get_blob_properties()

                            # Print the size of the blob
                            blob_size = blob_properties.size
                            print(f"{blob_name} size: {blob_size} bytes")
                    except Exception as e:
                        print("permission denied")
    # blob_service_client = BlobServiceClient(account_url=f"https://{account.name}.blob.core.windows.net", credential=helper.credential)
    # blob_client = blob_service_client.get_blob_client(container=container, blob="test.txt")
    #


def download_blob():
    helper = BlobHelper()
    storage_account_name = "saildevdatasets"
    container_name = "physionet"
    blob_name = "deidentified-medical-text-1.0/id.res"
    blob_client = helper.get_blob_client(storage_account_name, container_name, blob_name)
    helper.download_blob_to_file(blob_client, "temp.zip", verbose=True)


# deidentified - medical - text - 1.0 / LICENSE.txt

if __name__ == "__main__":
    print_storage(False)
    download_blob()
