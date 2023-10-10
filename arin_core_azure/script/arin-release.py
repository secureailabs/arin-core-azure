import os
import shutil
import subprocess
import sys


def usage() -> None:
    print("Usage: python arin-release.py [patch, minor, major], [code, docker, all]")


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

    # get version
    result = subprocess.run("python setup.py --version", capture_output=True, shell=True)
    current_version = result.stdout.decode("utf-8").strip()
    print(f"current verson: {current_version}")

    # get latest tagged version #TODO figure out how to deal with patches
    result = subprocess.run("git tag", capture_output=True, shell=True)
    tagged_versions = result.stdout.decode("utf-8").strip().split("\n")
    latest_tagged_version = tagged_versions[-1]
    print(f"latest tagged version: {latest_tagged_version}")

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
