import asyncio
from concurrent.futures import TimeoutError as ConnectionTimeoutError
from time import sleep

import websockets


connect_url = 'ws://localhost:8765'
timeout = 10  

class WebSocketClient(object):
    def __init__(self):
        self.conn = None

    async def connect(self, url):
        self.conn = await websockets.connect(url)
        return self.conn

    async def send(self, msg):
        await self.conn.send(msg)

    async def receive(self):
        await self.conn.rcv()

    async def close(self):
        await self.conn.close()

async def main():
    # handler = WebSocketClient()
    # await handler.connect(connect_url)
    # await handler.send('hello')
    # data = await handler.receive()
    # print(str(data))
    # await handler.send('hello2')
    # await asyncio.sleep(5)
    # await handler.close()
    async with websockets.connect(connect_url) as websocket:
        try:
            await websocket.send('test')
            print(await websocket.recv())
        except websockets.ConnectionClosed:
            s = ''
            #continue

asyncio.run(main())