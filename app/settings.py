import os


def get_archive_names(index: int = 0):
    while True:
        index += 1
        yield f"internal_{index}.7z"


root = os.path.abspath(".")
DEFAULT_ARCHIVE_NAMES = get_archive_names()
DEFAULT_FILE_STORAGE = os.path.join(root, "data")


def find_file(file_name: str, base_dir: str = root):
    for obj in os.listdir(base_dir):
        path = os.path.join(base_dir, obj)
        if obj == file_name:
            return path
        elif os.path.isdir(path):
            return find_file(file_name, path)
