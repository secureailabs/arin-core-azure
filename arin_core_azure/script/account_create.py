from arin_core_azure.cognitive_services_helper import CognitiveServicesHelper

helper = CognitiveServicesHelper()
list_account = helper.account_list_for_kind("OpenAI")
# helper.account_create(account)
