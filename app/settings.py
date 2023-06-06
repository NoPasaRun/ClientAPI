import os


root = os.path.abspath(".")


def find_file(file_name: str, base_dir: str = root):
    for obj in os.listdir(base_dir):
        path = os.path.join(base_dir, obj)
        if obj == file_name:
            return path
        elif os.path.isdir(path):
            return find_file(file_name, path)
