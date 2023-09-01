import os
import re
import subprocess

from arin_core_azure.env_tools import read_package_init
from arin_core_azure.script.build_docker import build_docker
from arin_core_azure.script.start_docker import start_docker


def main() -> None:
    dict_init = read_package_init()
    image_version = dict_init["__version__"]
    title = dict_init["__title__"]
    image_name = f"arin/{title}-image"
    conainer_name = f"{title}-container"
    print(image_version)
    build_docker(image_name, image_version)
    start_docker(image_name, image_version, conainer_name)


if __name__ == "__main__":
    main()
