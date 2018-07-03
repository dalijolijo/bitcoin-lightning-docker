import asyncio
import os

import websockets

async def client(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            if message == 'ping':
                await websocket.send('pong')
            elif message:
                print(message)

host = os.environ.get('WEBSOCKET_HOST', '127.0.0.1')
port = os.environ.get('WEBSOCKET_PORT', 8765)
asyncio.get_event_loop().run_until_complete(client(f'ws://{host}:{port}'))
