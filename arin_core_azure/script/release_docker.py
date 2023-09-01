# function to tag and push the input image to the docker hub
import os
import re
import subprocess

from arin_core_azure.env_tools import read_package_init
from arin_core_azure.script.build_docker import build_docker


def main() -> None:
    dict_init = read_package_init()
    version = dict_init["__version__"]
    title = dict_init["__title__"]
    project_name = title
    image_name = f"arin/{project_name}-image"
    image_tag = version
    conainer_name = f"{project_name}-container"
    build_docker(image_name, image_tag)
    push_image_to_registry(image_name, image_tag)


def push_image_to_registry(image_name: str, image_tag: str):
    # check docker installed
    DOCKER_REGISTRY_NAME = os.environ["DOCKER_REGISTRY_NAME"]
    AZURE_CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
    AZURE_CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]
    AZURE_TENANT_ID = os.environ["AZURE_TENANT_ID"]
    AZURE_SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
    image_name_tag = f"{image_name}:{image_tag}"

    # echo "login to azure account"
    command = f"az login --service-principal --username {AZURE_CLIENT_ID} --password {AZURE_CLIENT_SECRET} --tenant {AZURE_TENANT_ID}"
    print(command)
    subprocess.run(command, shell=True)
    command = f"az account set --subscription {AZURE_SUBSCRIPTION_ID}"
    print(command)
    subprocess.run(command, shell=True)

    command = f"az acr login --name {DOCKER_REGISTRY_NAME}"
    print(command)
    subprocess.run(command, shell=True)

    command = f"docker tag {image_name_tag} {DOCKER_REGISTRY_NAME}.azurecr.io/{image_name_tag}"
    subprocess.run(command, shell=True)
    print(command)

    command = f"docker push {DOCKER_REGISTRY_NAME}.azurecr.io/{image_name_tag}"
    print(command)
    subprocess.run(command, shell=True)


if __name__ == "__main__":
    main()
