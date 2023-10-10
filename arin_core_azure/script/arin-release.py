import json
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

    if len(sys.argv) == 4:  # TODO commig changes
        print("ignoring changes")
        check_changes = False
    else:
        check_changes = True

    # check if there are open git changes
    if check_changes:
        result = subprocess.run("git status --porcelain", capture_output=True, shell=True)
        if result.stdout.decode("utf-8") != "":
            print("Below is a list of open git changes. Please commit or stash them.")
            print(result.stdout.decode("utf-8"))
            sys.exit(1)

    # get package name
    with open("setup.py", "r") as f:
        file_contents = f.read()

    # read setup config
    dict_config = read_setup_config()

    # read release config
    with open("release.json", "r") as f:
        release_config = json.load(f)

    # get module name
    module_name = dict_config["version_variable"].split("/")[0]
    print(f"module name: {module_name}")

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
            # TODO only tag if there are changes
            target_version = bump_version(current_version, release_type)
            print(f"Latest tagged version match current version. Bumping and releasing as as {target_version}")

            # update version in init.py
            with open(f"{module_name}/__init__.py", "r") as f:
                file_contents = f.read()
            file_contents = file_contents.replace(current_version, target_version)
            with open(f"{module_name}/__init__.py", "w") as f:
                f.write(file_contents)

            # commit version bump
            print("commit changes version bump")
            subprocess.run(f"git add {module_name}/__init__.py")
            subprocess.run(f'git commit -m "bump version to {target_version}"', shell=True)
            subprocess.run(f"git push", shell=True)

    # tag version
    subprocess.run(f"git tag {target_version}")
    subprocess.run(f"git push origin {target_version}")

    # remove old build
    shutil.rmtree("dist", ignore_errors=True)

    # build dist
    subprocess.run(f"python setup.py bdist_wheel")

    # upload result
    for code_release_target in release_config["list_code_release_target"]:
        release_target_type = code_release_target["release_target_type"]
        if release_target_type == "pypi":
            repository_url = code_release_target["repository_url"]
            username = code_release_target["username"]
            password = code_release_target["password"]

            list_name_file = os.listdir("dist")
            print(list_name_file)
            for name_file in list_name_file:
                if name_file.endswith(".whl"):
                    path_file = os.path.join("dist", name_file)
                    subprocess.run(
                        f"twine upload {path_file} --repository-url {repository_url} --username {username} --password {password}"
                    )
        else:
            print(f"release_target_type {release_target_type} not supported")


if __name__ == "__main__":
    main()
