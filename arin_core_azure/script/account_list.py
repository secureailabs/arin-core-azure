from arin_core_azure.cognitive_services_helper import CognitiveServicesHelper

helper = CognitiveServicesHelper()
list_account = helper.account_list_for_kind("OpenAI")
for account in list_account:
    subscription_id, resource_group_name, account_name = helper.account_get_locator_data(account)
    print(subscription_id)
    print(resource_group_name)
    print(account_name)
