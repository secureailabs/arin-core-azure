import os
import subprocess


def main() -> None:
    docker_registry_url = "developmentdockerregistry.azurecr.io"
    docker_registry_username = "DevelopmentDockerRegistry"
    docker_registry_password = "5ojmm/LV00J6xaqwlMODyE0srZ1PhBm/jB0zofAxiu+ACRDjKbya"
    command = f"sudo docker login {docker_registry_url} --username {docker_registry_username} --password {docker_registry_password}"
    print(command)


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
