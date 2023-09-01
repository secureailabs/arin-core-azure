import re

from setuptools import find_packages, setup

version = ""
with open("arin_core_azure/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)  # type: ignore

requirements = []
with open("requirements.txt") as file:
    requirements = file.read().splitlines()

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="arin-core-azure",
    version=version,
    install_requires=requirements,
    packages=find_packages(),
    package_data={},
    python_requires=">=3.8",
    author="Jaap Oosterbroek",
    author_email="jaap@secureailabs.com",
    description="A library to support the sail llm projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://nowhere.not",
    entry_points={
        "console_scripts": [
            "build_docker=arin_core_azure.script.build_docker:main",
            "release_docker=arin_core_azure.script.release_docker:main",
            "deploy_docker_local=arin_core_azure.script.deploy_docker_local:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: SAIL :: Propritary",
        "Operating System :: OS Independent",
    ],
)
