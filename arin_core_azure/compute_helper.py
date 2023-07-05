from typing import List, Optional, Tuple

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachine
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient

from arin_core_azure.base_helper import BaseHelper


class ComputeHelper(BaseHelper):
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        super().__init__(client_id, client_secret, tenant_id)
        # Initialize the subscription client
        self.subscription_client = SubscriptionClient(self.credential)

    def list_vm(self, subscription_id: str) -> List[VirtualMachine]:
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        list_vm = []
        for vm in compute_client.virtual_machines.list_all():
            list_vm.append(vm)
        return list_vm

    def list_vm_with_tag(self, subscription_id: str, tag_key: str, tag_value: str) -> List[VirtualMachine]:
        # TODO there should be a faster way of doign this
        list_vm = []
        for vm in self.list_vm(subscription_id):
            if vm.tags is not None:
                if tag_key in vm.tags:
                    if vm.tags[tag_key] == tag_value:
                        list_vm.append(vm)
        return list_vm

    def find_vms_of_type(self, subscription_id: str, vm_size: str) -> List[VirtualMachine]:
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        vms = compute_client.virtual_machines.list_all()
        # Iterate over each virtual machine
        list_of_vms = []
        for vm in vms:
            if vm.hardware_profile.vm_size == vm_size:
                list_of_vms.append(vm)

        return list_of_vms

    def get_vm_key_data(self, vm: VirtualMachine) -> str:
        return vm.os_profile.linux_configuration.ssh.public_keys[0].key_data
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        return compute_client.virtual_machines.list_secrets(resource_group_name, virtual_machine_name).instance_view

    def get_vm_hostname(self, vm: VirtualMachine) -> str:
        return vm.os_profile.computer_name  # type: ignore

    def get_network_interface_name(self, vm: VirtualMachine) -> str:
        network_profile = vm.network_profile
        if network_profile is None:
            raise ValueError(f"Network profile not found for VM {vm.name}")
        network_interface_id = network_profile.network_interfaces[0].id
        return str(network_interface_id).split("/")[-1]

    def get_vm_admin_username(self, vm: VirtualMachine) -> str:
        return vm.os_profile.admin_username

    def get_vm_public_ip_address(self, vm: VirtualMachine) -> str:
        # get clients
        subscription_id, resource_group_name, virtual_machine_name = self.get_vm_locator(vm)
        network_client = NetworkManagementClient(self.credential, subscription_id)
        network_interface_name = self.get_network_interface_name(vm)
        network_interface = network_client.network_interfaces.get(resource_group_name, network_interface_name)
        for ip_configuration in network_interface.ip_configurations:
            if ip_configuration.public_ip_address is not None:
                public_ip_address_name = ip_configuration.public_ip_address.name
                public_ip_address = network_client.public_ip_addresses.get(resource_group_name, public_ip_address_name)
                ip_address = public_ip_address.ip_address
                return ip_address
        raise ValueError(f"Public IP address not found for VM {vm.name}")

    def get_vm_by_name(
        self, subscription_id: str, resource_group_name: str, virtual_machine_name: str
    ) -> VirtualMachine:
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        return compute_client.virtual_machines.get(resource_group_name, virtual_machine_name)  # type: ignore

    def get_vm_locator(self, vm: VirtualMachine) -> Tuple[str, str, str]:
        id_part = str(vm.id).split("/")
        subscription_id = id_part[2]
        resource_group_name = id_part[4]
        virtual_machine_name = id_part[8]
        return subscription_id, resource_group_name, virtual_machine_name

    def get_vm_resource_group_name(self, vm: VirtualMachine) -> str:
        return str(vm.id).split("/")[4]

    def get_vm_status_by_name(self, subscription_id: str, resource_group_name: str, virtual_machine_name: str):
        """
        this will just return the status of the virtual machine
        sometime the status may be unknown as shown by the azure portal;
        in that case statuses[1] doesn't exist, hence retrying on IndexError
        also, it may take on the order of minutes for the status to become
        available so the decorator will bang on it forever
        """
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        return (
            compute_client.virtual_machines.get(resource_group_name, virtual_machine_name, expand="instanceView")
            .instance_view.statuses[1]
            .display_status
        )

    def get_vm_status(self, subscription_id, resource_group_name, virtual_machine_name):
        """
        this will just return the status of the virtual machine
        sometime the status may be unknown as shown by the azure portal;
        in that case statuses[1] doesn't exist, hence retrying on IndexError
        also, it may take on the order of minutes for the status to become
        available so the decorator will bang on it forever
        """
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        return (
            compute_client.virtual_machines.get(resource_group_name, virtual_machine_name, expand="instanceView")
            .instance_view.statuses[1]
            .display_status
        )

    def start_vm(
        self,
        subscription_id: str,
        resource_group_name: str,
        virtual_machine_name: str,
        wait: bool = True,
        verbose: bool = True,
    ):
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        # Start the virtual machine
        if verbose:
            print("starting vm")
        async_vm_start = compute_client.virtual_machines.begin_start(resource_group_name, virtual_machine_name)
        if wait:
            if verbose:
                while not async_vm_start.done():
                    print(".")
                    async_vm_start.wait(1)
            else:
                async_vm_start.wait()
        if verbose:
            print("vm start complete")

    def stop_vm(
        self,
        subscription_id: str,
        resource_group_name: str,
        virtual_machine_name: str,
        wait: bool = True,
        verbose: bool = True,
    ):
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        # create three system beep sounds to warn the user

        print("\a")
        print("\a")
        print("\a")
        print("Warning this will stop the VM but it will not stop billing")

        # Stop the virtual machine
        if verbose:
            print("stopping vm")
        async_vm_power_off = compute_client.virtual_machines.begin_power_off(resource_group_name, virtual_machine_name)
        if wait:
            if verbose:
                while not async_vm_power_off.done():
                    print(".")
                    async_vm_power_off.wait(1)
            else:
                async_vm_power_off.wait()
        if verbose:
            print("vm stop done")

    def deallocate_vm(
        self,
        subscription_id: str,
        resource_group_name: str,
        virtual_machine_name: str,
        wait: bool = True,
        verbose: bool = True,
    ):
        compute_client = ComputeManagementClient(self.credential, subscription_id)
        # Deallocate the VM
        if verbose:
            print("deallocating vm ")
        async_vm_deallocate = compute_client.virtual_machines.begin_deallocate(
            resource_group_name, virtual_machine_name
        )
        if wait:
            if verbose:
                while not async_vm_deallocate.done():
                    print(".")
                    async_vm_deallocate.wait(1)
            else:
                async_vm_deallocate.wait()
        if verbose:
            print("vm deallocating done")
