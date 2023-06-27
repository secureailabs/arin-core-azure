from dataclasses import dataclass

from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import AzureFirewallIPConfiguration, PublicIPAddress, PublicIPAddressSku, SubResource
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import Deployment, DeploymentMode, DeploymentProperties, ResourceGroup

# @dataclass
# class DeploymentInfo:
#     credentials: ClientSecretCredential
#     subscription_id: str
#     object_id: str
#     name: str
#     location: str
#     id: str


class SailAzure:
    def __init__(self, client_id: str, client_secret: str, tenant_id: str) -> None:
        """Authenticate using client_id and client_secret."""
        self.credential = ClientSecretCredential(client_id=client_id, client_secret=client_secret, tenant_id=tenant_id)

    def create_resource_group(self, subscription_id: str, resource_group_name: str, location: str):
        client = ResourceManagementClient(self.credential, subscription_id)
        response = client.resource_groups.create_or_update(
            resource_group_name,
            parameters=ResourceGroup(
                location=location,
                tags={
                    "deployed_method": "DeployPlatform",
                },
            ),
        )
        assert response.properties is not None  # TODO this seems weird
        return response.properties.provisioning_state

    def deploy_template(self, subscription_id: str, resource_group_name: str, template: str, parameters: str):
        """Deploy the template to a resource group."""
        client = ResourceManagementClient(self.credential, subscription_id)

        parameters = {k: {"value": v} for k, v in parameters.items()}
        deployment_properties = DeploymentProperties(
            mode=DeploymentMode.INCREMENTAL, template=template, parameters=parameters
        )
        deployment_async_operation = client.deployments.begin_create_or_update(
            resource_group_name, "azure-sample", Deployment(properties=deployment_properties)
        )
        deployment_async_operation.wait()

        return deployment_async_operation.status()

    def delete_resouce_group(self, subscription_id: str, resource_group_name: str):
        client = ResourceManagementClient(self.credential, subscription_id)
        delete_async_operation = client.resource_groups.begin_delete(resource_group_name)
        delete_async_operation.wait()

        print(delete_async_operation.status())

    def get_public_ip(self, subscription_id: str, resource_group_name: str, ip_resource_name: str) -> str:
        """Get the IP address of the resource."""
        client = NetworkManagementClient(self.credential, subscription_id)
        public_ip_address = client.public_ip_addresses.get(resource_group_name, ip_resource_name)
        return public_ip_address.ip_address

    def get_private_ip(self, subscription_id: str, resource_group_name: str, network_interface_name: str) -> str:
        """Get the private IP of the virtual machine."""
        client = NetworkManagementClient(self.credential, subscription_id)
        private_ip_address = client.network_interfaces.get(resource_group_name, network_interface_name)
        if private_ip_address.ip_configurations is None:
            raise Exception("No IP configuration found")

        if private_ip_address.ip_configurations[0].private_ip_address is None:
            raise Exception("No private IP address found")

        return private_ip_address.ip_configurations[0].private_ip_address

    def create_public_ip(
        self, subscription_id: str, resource_group_name: str, ip_resource_name: str, location: str
    ) -> PublicIPAddress:
        client = NetworkManagementClient(self.credential, subscription_id)

        # Create Public ip resource
        params = PublicIPAddress(
            location=location,
            sku=PublicIPAddressSku(name="standard", tier="regional"),
            public_ip_allocation_method="static",
            public_ip_address_version="ipv4",
        )

        deployment_async_operation = client.public_ip_addresses.begin_create_or_update(
            resource_group_name, ip_resource_name, params
        )
        deployment_async_operation.wait()
        print(f"deployment_async_operation result:, {deployment_async_operation.result()}")
        print(f"IP creation status: {deployment_async_operation.status()}")

        return deployment_async_operation.result()

    def update_fw_pip(self, subscription_id: str, firewall_ip: PublicIPAddress):
        client = NetworkManagementClient(self.credential, subscription_id)
        fw_info = client.azure_firewalls.get("rg-sail-wus-hub-001", "afw-sail-wus")
        fw_policy_info = client.firewall_policies.get("rg-sail-wus-hub-001", "afwpol-sail-wus-001")

        print(f"fw_info:\n {fw_info.as_dict()}\n")
        print(f"fw_info ip_configurations:\n {fw_info.ip_configurations}\n")
        print(f"fw_policy_info:\n {fw_policy_info.as_dict()}\n")
        print("\n\n===============================================================")
        # Update firewall with a specific new public ip address
        if fw_info.ip_configurations is None:
            fw_info.ip_configurations = []

        ip_config = AzureFirewallIPConfiguration(
            id=firewall_ip.id, name=firewall_ip.name, public_ip_address=SubResource(id=firewall_ip.id)
        )
        fw_info.ip_configurations.append(ip_config)

        async_updated_fw_pip_result = client.azure_firewalls.begin_create_or_update(
            "rg-sail-wus-hub-001", "afw-sail-wus", fw_info
        ).result()
        print(async_updated_fw_pip_result)
        print("Updated a new Firewall Public ip to Firewall ip configuration")
        print("\n\n===============================================================")

    def update_nat_rule_policy(self, firewall_ip: PublicIPAddress, private_ip_address: str, port: str):
        nat_rule_policy = {
            "name": f"{firewall_ip.name}_{port}",
            "rule_type": "NatRule",
            "ip_protocols": ["TCP"],
            "source_addresses": ["*"],
            "destination_addresses": [firewall_ip.ip_address],
            "destination_ports": [port],
            "translated_address": private_ip_address,
            "translated_port": port,
            "source_ip_groups": [],
        }

        print("nat_rule_policy", nat_rule_policy)
        return nat_rule_policy

    def update_fw_dnat_rules(self, subscription_id: str, firewall_ip: PublicIPAddress, private_ip_address: str):
        client = NetworkManagementClient(self.credential, subscription_id)
        # Get current information on policies in rule collection groups
        fw_api_policy_rule_collection_info = client.firewall_policy_rule_collection_groups.get(
            "rg-sail-wus-hub-001",
            "afwpol-sail-wus-001",
            "APIRuleCollectionGroup",
        )

        # Update DNAT rule in Firewall for module
        if fw_api_policy_rule_collection_info.rule_collections is None:
            raise Exception("No rule collections found in APIRuleCollectionGroup")

        fw_api_policy_rule_collection_info.rule_collections[0].rules.append(  # type: ignore
            self.update_nat_rule_policy(firewall_ip, private_ip_address, "443")
        )

        async_updated_fw_pol_result = client.firewall_policy_rule_collection_groups.begin_create_or_update(
            "rg-sail-wus-hub-001",
            "afwpol-sail-wus-001",
            "APIRuleCollectionGroup",
            fw_api_policy_rule_collection_info,
        ).result()
        print(f"Updated a new Firewall DNAT RULE")
        return async_updated_fw_pol_result
