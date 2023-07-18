import os


def get_dir_from_env(
    environment_variable: str,
    create_if_missing=False,
    exception_if_missing=True,
) -> str:
    if environment_variable not in os.environ:
        raise ValueError(f"environment variable {environment_variable} not found")
    path_dir = os.environ[environment_variable]
    if not os.path.isdir(path_dir):
        if create_if_missing:
            os.makedirs(path_dir)
        else:
            if exception_if_missing:
                raise ValueError(f"directory {path_dir} not found")
    return path_dir


def get_string_from_env(
    environment_variable: str,
):
    if environment_variable not in os.environ:
        raise ValueError(f"environment variable {environment_variable} not found")
    return os.environ[environment_variable]
