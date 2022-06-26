import asyncio
import functools
import logging
import string
from time import sleep

import websockets

from websockets import server

from multiprocessing import Pipe

logging.basicConfig(level=logging.INFO)

class WebSocketServer():
    clients = set()

    __server = None

    def __init__(self, host = '', port = '', handler = ''):
        self.host    = host
        self.port    = port
        self.handler = handler

    async def start_server(self):
       #handler = functools.partial(self.client_handler, websocket = None)
       self.__server = await server.serve(self.handler, self.host, self.port)
    
    async def client_handler(self, websocket: server.WebSocketServerProtocol):
        while(True):
            print(await websocket.recv())
        #print('HELLO', websocket)

        #message = await websocket.recv()

        #print(message)

        # async for message in websocket:
        #     print(message)
        # async for message in websocket:
        #     await websocket.send(message)
        # async for message in websocket:
        #     print(message)
        #     websocket.send('Test')

    def stop_server(self):
        return self.__server.close()

    async def send(self, data: any):
        await asyncio.wait([client.send(data) for client in self.clients])

    def receive(self):
        return
    
    def isAlive(self) -> bool:
        return self.__server.sockets

# async def ws_handler(websocket, pipe: Pipe):
#     async for message in websocket:
#         print(message)
        #pipe3.send()

# async def ws_server(pipe):
#     ws_handler_partial = functools.partial(ws_handler, pipe = pipe)

#     async with websockets.serve(ws_handler_partial, "localhost", 8000):
#         await asyncio.Future()



# import asyncio
# import functools
# import logging
# import string
# from time import sleep

# import websockets

# from websockets import server

# from multiprocessing import Pipe

# logging.basicConfig(level=logging.INFO)

# async def client_handler(websocket: server.WebSocketServerProtocol):
#     print('HELLO SOCKET')
#     while(True):
#         print(await websocket.recv())

# async def start_ws_server():
#     async with websockets.serve(client_handler, "localhost", 8765):
#         await asyncio.Future()  # run forever
