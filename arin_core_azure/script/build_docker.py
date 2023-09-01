import os
import re
import subprocess

from arin_core_azure.env_tools import read_package_init


def main() -> None:
    dict_init = read_package_init()
    version = dict_init["__version__"]
    title = dict_init["__title__"]
    image_name = f"arin/{title}-image"
    image_version = version
    conainer_name = f"{title}-container"
    print(image_version)
    build_docker(image_name, image_version)


def build_docker(image_name: str, image_version: str):
    image_tag = f"{image_name}:{image_version}"
    dict_build_args = {}
    dict_build_args["ARIN_PYPI_REPOSITORY_URL"] = os.environ.get("ARIN_PYPI_REPOSITORY_URL")
    dict_build_args["ARIN_PYPI_USERNAME"] = os.environ.get("ARIN_PYPI_USERNAME")
    dict_build_args["ARIN_PYPI_PASSWORD"] = os.environ.get("ARIN_PYPI_PASSWORD")

    build_command = f"docker build -t {image_tag}"
    build_command += " --progress=plain"
    for key, value in dict_build_args.items():
        build_command += f" --build-arg {key}={value}"
    build_command += " ."
    print(build_command)
    subprocess.call(build_command, shell=True)


if __name__ == "__main__":
    main()
