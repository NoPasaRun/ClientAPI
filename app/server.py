import os
from app.settings import root

import aiofiles
from aiohttp import web


DEFAULT_SERVER_STORAGE = os.path.join(root, "server_files")


async def send_file(request):
    name = request.match_info.get("name")
    if name is not None:
        path = os.path.join(DEFAULT_SERVER_STORAGE, name)
        if os.path.exists(path):
            async with aiofiles.open(path, 'rb') as file:
                data = await file.read()
    return web.Response(body=data)

app = web.Application()
app.add_routes([web.get('/api/files/{name}', send_file)])

if __name__ == '__main__':
    web.run_app(app)
