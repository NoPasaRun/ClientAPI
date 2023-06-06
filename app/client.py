import os
import yaml
import zipfile
import py7zr

import asyncio
import aiohttp
import aiofiles

from typing import List, Dict, Callable

from app.settings import find_file, DEFAULT_FILE_STORAGE


def parse_config(file_name):
    assert file_name.endswith("yaml") is True
    path = find_file(file_name)
    with open(path) as data_file:
        return yaml.safe_load(data_file)


CONFIG: Dict = parse_config("config.yaml")
HOST, TARGET = CONFIG.get("host"), CONFIG.get("target")


class API:

    __protocol: str = "http"

    def __init__(self, **kwargs):
        self.__host: str = kwargs.get("host")
        self.__target: str = kwargs.get("target")

    @property
    def route(self) -> str:
        route = "/".join([string for string in self.__target.split("/") if string != ""])
        return route

    @property
    def host(self) -> str:
        return self.__host

    @property
    def url(self) -> str:
        return f"{self.__protocol}://{self.host}/{self.route}"

    async def send_request(self, file_name: str):
        async with self.__session.get(f"{self.url}/{file_name}") as response:
            return await response.content.read()

    async def __aenter__(self):
        self.__session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.__session.close()


def await_unpack(function: Callable):
    async def wrapper(self: 'FileManager', *args, **kwargs):
        for archive in filter(lambda obj: obj is not None, [FileManager.exist(name) for name in self.dependencies]):
            while True:
                if archive.unpacked:
                    await function(self, *args, **kwargs)
                    break
                await asyncio.sleep(0.001)
        else:
            await function(self, *args, **kwargs)
    return wrapper


class FileManager:

    __files: Dict = {}
    __classes = {
        ".7z": py7zr.SevenZipFile,
        ".zip": zipfile.ZipFile
    }

    def __init__(self, **kwargs):
        self.__name: str = kwargs.get("name")
        assert self.__name != ""
        self.__file_name: str = kwargs.get("file")
        self.__actions: List = [getattr(self, action) for action in kwargs.get("actions", [])]
        self.__dependencies = kwargs.get("dependencies", [])
        self.__unpacked = False

        FileManager.__files[self.__name] = self

    @property
    def name(self):
        return self.__name

    @property
    def unpacked(self):
        return self.__unpacked

    @property
    def actions(self):
        return self.__actions

    @property
    def dependencies(self):
        return self.__dependencies

    @classmethod
    def exist(cls, name: str) -> 'FileManager':
        return cls.__files.get(name)

    def __new__(cls, name: str, **kwargs) -> 'FileManager':
        obj: 'FileManager' = cls.exist(name)
        if obj:
            return obj
        return super(FileManager, cls).__new__(cls)

    async def save(self, byte_array: bytes):
        async with aiofiles.open(os.path.join(DEFAULT_FILE_STORAGE, self.__file_name), "wb") as f:
            await f.write(byte_array)

    async def download(self):
        async with API(host=HOST, target=TARGET) as api:
            content: bytes = await api.send_request(self.__file_name)
            await self.save(content)

    @await_unpack
    async def unpack(self):
        ext = "." + self.__file_name.split(".")[-1]
        zip_class = self.__classes.get(ext)
        with zip_class(os.path.join(DEFAULT_FILE_STORAGE, self.__file_name), "r") as zip_ref:
            zip_ref.extractall(DEFAULT_FILE_STORAGE)
        self.__unpacked = True


if __name__ == '__main__':
    for file_data in CONFIG.get("files", []):
        file = FileManager(**file_data)
        for func in file.actions:
            asyncio.run(func())

