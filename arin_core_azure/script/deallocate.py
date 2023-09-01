import sys

from arin_core_azure.compute_helper import ComputeHelper
from arin_core_azure.resource_helper import ResourceHelper

# get username form command line
username = sys.argv[1]
# get purpose form command line
# purpose = sys.argv[2]

compute_helper = ComputeHelper()
resource_helper = ResourceHelper()

subscription_name = "Development"
subscription_id = resource_helper.get_subscription_id(subscription_name)
list_vm = compute_helper.list_vm_with_tag(subscription_id, "Owner", username)
for vm in list_vm:

    tags = compute_helper.vm_get_tags(vm)
    if "Purpose" in tags:
        if tags["Purpose"] == "pipyserver":
            print("Skipping pipyserver")
            continue
    print(f"Deallocating VM {vm.name}")

    resource_group_name = compute_helper.get_vm_resource_group_name(vm)
    compute_helper.deallocate_vm(subscription_id, resource_group_name, vm.name)
