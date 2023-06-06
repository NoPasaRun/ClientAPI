import yaml

import aiohttp
import asyncio

from typing import List, Dict

from app.settings import find_file


class API:

    __protocol: str = "http"

    def __init__(self, **kwargs):
        self.__host: str = kwargs.get("host")
        self.__route: str = kwargs.get("route")

    @property
    def route(self) -> str:
        if self.__route.startswith("/"):
            return self.__route.replace("/", "")
        return self.__route

    @property
    def host(self) -> str:
        return self.__host

    @property
    def url(self) -> str:
        return f"{self.__protocol}://{self.host}/{self.route}"


def run_dependence(function):
    def wrapper(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)


@run_dependence
class FileManager:

    __files: Dict = {}

    def __init__(self, name: str, **kwargs):
        self.__name: str = name
        self.__file_name: str = kwargs.get("file_name")
        self.__actions: List = [getattr(self, action) for action in kwargs.get("actions", [])]
        self.__dependencies = filter([FileManager.exist(depend) for depend in kwargs.get("dependencies")])

        FileManager.__files[self.__name] = self

    @classmethod
    def exist(cls, name: str) -> 'FileManager':
        return cls.__files.get(name)

    def __new__(cls, name: str, **kwargs) -> 'FileManager':
        obj: 'FileManager' = cls.exist(name)
        if obj:
            return obj
        return super(FileManager, cls).__new__(cls)

    @run_dependence
    def download(self, api: API):
        pass

    @run_dependence
    def unpack(self):
        pass


def parse_config(file_name):
    assert file_name.endswith("yaml") is True
    path = find_file(file_name)
    with open(path) as data_file:
        return yaml.safe_load(data_file)


if __name__ == '__main__':
    file_manager = FileManager("my_archive")
