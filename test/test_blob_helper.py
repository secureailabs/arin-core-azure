from arin_core_azure.resource_helper import ResourceHelper
from arin_core_azure.blob_helper import BlobHelper

resource_helper = ResourceHelper()
list_subscription = resource_helper.list_subscription()
helper = BlobHelper()

helper.list_container()
helper.download_blob_to_file(