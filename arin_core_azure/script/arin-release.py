import os
import shutil
import subprocess
import sys


def read_setup_config() -> dict:
    with open("setup.cfg", "r") as f:
        file_contents = f.read()
    config = {}
    for line in file_contents.split("\n"):
        if "=" in line:
            key, value = line.split("=")
            config[key.strip()] = value.strip()
    return config


def usage() -> None:
    print("Usage: python arin-release.py [patch, minor, major], [code, docker, all]")


def bump_version(version: str, release_type: str) -> str:
    version_parts = version.split(".")
    if release_type == "patch":
        version_parts[2] = str(int(version_parts[2]) + 1)
    elif release_type == "minor":
        version_parts[1] = str(int(version_parts[1]) + 1)
        version_parts[2] = "0"
    elif release_type == "major":
        version_parts[0] = str(int(version_parts[0]) + 1)
        version_parts[1] = "0"
        version_parts[2] = "0"
    return ".".join(version_parts)


def main() -> None:
    # check arguments and set default values
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)
    release_type = sys.argv[1]
    if release_type not in ["patch", "minor", "major"]:
        usage()
        sys.exit(1)
    release_target = sys.argv[2]
    if release_target not in ["code", "docker", "all"]:
        usage()
        sys.exit(1)

    # check if there are open git changes
    result = subprocess.run("git status --porcelain", capture_output=True, shell=True)
    if result.stdout.decode("utf-8") != "":
        print("Below is a list of open git changes. Please commit or stash them.")
        print(result.stdout.decode("utf-8"))
        sys.exit(1)
    # get package name
    with open("setup.py", "r") as f:
        file_contents = f.read()
    dict_config = read_setup_config()
    package_name = dict_config["version_variable"].split("/")[0]
    print(package_name)
    exit()
    package_name = file_contents.split("name='")[1].split("'")[0]
    print(f"package name: {package_name}")

    # get version
    result = subprocess.run("python setup.py --version", capture_output=True, shell=True)
    current_version = result.stdout.decode("utf-8").strip()
    print(f"current verson: {current_version}")

    # get latest tagged version #TODO figure out how to deal with patches
    result = subprocess.run("git tag", capture_output=True, shell=True)
    tagged_versions = result.stdout.decode("utf-8").strip().split("\n")
    target_version = ""
    if (len(tagged_versions) == 0) or (len(result.stdout.decode("utf-8").strip()) == 0):
        target_version = current_version
        print(f"No tagged versions found. Releasing as {target_version}")
    else:
        latest_tagged_version = tagged_versions[-1]
        print(f"Latest tagged version: {latest_tagged_version}")
        if latest_tagged_version != current_version:
            target_version = current_version
            print(f"Latest tagged version does not match current version. Releasing as {target_version}")
        else:
            target_version = bump_version(current_version, release_type)
            print(f"Latest tagged version match current version. Bumping and releasing as as {target_version}")

    # update version in init.py
    with open(f"{package_name}/__init__.py", "r") as f:
        file_contents = f.read()
    file_contents = file_contents.replace(current_version, target_version)
    with open(f"{package_name}/__init__.py", "w") as f:
        f.write(file_contents)
    exit()

    # commit changes
    print("commit changes version bump")
    subprocess.run(f"git add {package_name}/__init__.py")
    subprocess.run(f"git commit -m 'bump version to {target_version}'")

    # tag version
    # subprocess.run(f"git tag {target_version}")
    # subprocess.run(f"git push origin {target_version}")

    # ARIN_PYPI_REPOSITORY_URL = os.environ["ARIN_PYPI_REPOSITORY_URL"]
    # ARIN_PYPI_USERNAME = os.environ["ARIN_PYPI_USERNAME"]
    # ARIN_PYPI_PASSWORD = os.environ["ARIN_PYPI_PASSWORD"]

    # # remove old build
    # shutil.rmtree("dist", ignore_errors=True)

    # # build dist
    # subprocess.run(f"python setup.py bdist_wheel")

    # # upload result
    # list_name_file = os.listdir("dist")
    # print(list_name_file)
    # for name_file in list_name_file:
    #     if name_file.endswith(".whl"):
    #         path_file = os.path.join("dist", name_file)
    #         subprocess.run(
    #             f"twine upload {path_file} --repository-url {ARIN_PYPI_REPOSITORY_URL} --username {ARIN_PYPI_USERNAME} --password {ARIN_PYPI_PASSWORD}"
    #         )


if __name__ == "__main__":
    main()
