import os


def read_package_init() -> dict:
    with open("module_name.txt", "r") as file:
        module_name = file.read()
    path_file_init_file = os.path.join(module_name, "__init__.py")
    with open(path_file_init_file, "r") as file:
        list_line = file.readlines()
    dict_init = {}
    for line in list_line:
        if line.startswith("__"):
            key, value = line.split("=")
            key = key.strip()
            value = value.split("#")[0]
            value = value.strip()
            value = value.strip('"')
            dict_init[key] = value
    return dict_init


def get_dir_from_env(
    environment_variable: str,
    create_if_missing=False,
    exception_if_missing=True,
) -> str:
    if environment_variable not in os.environ:
        raise ValueError(f"Environment variable {environment_variable} not found")
    path_dir = os.environ[environment_variable]
    if not os.path.isdir(path_dir):
        if create_if_missing:
            os.makedirs(path_dir)
        else:
            if exception_if_missing:
                raise ValueError(f"directory {path_dir} not found")
    return path_dir


def get_file_from_env(
    environment_variable: str,
    exception_if_missing=True,
) -> str:
    if environment_variable not in os.environ:
        raise ValueError(f"Environment variable {environment_variable} not found")
    path_file = os.environ[environment_variable]
    if not os.path.isfile(path_file) and exception_if_missing:
        raise ValueError(f"File {path_file} not found")
    return path_file


def get_string_from_env(
    environment_variable: str,
):
    if environment_variable not in os.environ:
        raise ValueError(f"environment variable {environment_variable} not found")
    return os.environ[environment_variable]


def get_string_from_file_from_env(
    environment_variable: str,
):
    path_file = get_file_from_env(environment_variable)
    with open(path_file, "r") as f:
        return f.read()
