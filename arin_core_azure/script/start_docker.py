import os
import re
import subprocess

from arin_core_azure.env_tools import read_package_init


def main() -> None:
    dict_init = read_package_init()
    version = dict_init["__version__"]
    title = dict_init["__title__"]
    image_name = f"arin/{title}-image"
    image_tag = version
    conainer_name = f"{title}-container"
    start_docker(image_name, image_tag, conainer_name)


def start_docker(image_name: str, image_tag: str, conainer_name: str):
    image_name_tag = f"{image_name}:{image_tag}"
    subprocess.call(f"docker stop {conainer_name}", shell=True)
    subprocess.call(f"docker rm {conainer_name}", shell=True)

    dict_env = {}
    dict_env["PATH_DIR_DATA_PATIENT_STORY"] = "/data/patient_story"
    dict_env["PATH_DIR_PROMPT_CACHE"] = "/data/prompt_cache"

    dict_env["PATH_FILE_FFMPEG"] = "/usr/bin/ffmpeg"
    dict_env["OPENAI_ENGINE_NAME"] = "gpt-4"
    dict_env["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    dict_env["AZURE_DATASET_CONNECTIONSTRING"] = os.environ.get("AZURE_DATASET_CONNECTIONSTRING")
    dict_env["AZURE_PROMPT_CONTAINER_NAME"] = os.environ.get("AZURE_PROMPT_CONTAINER_NAME")

    dict_mount = {}
    start_command = f"docker run -d --name {conainer_name}"
    for key, value in dict_env.items():
        start_command += f" -e {key}={value}"
    start_command += f" -p 8000:8000 {image_name_tag}"
    print(start_command)
    subprocess.call(start_command, shell=True)


if __name__ == "__main__":
    main()
