# -*- coding: utf-8 -*-
import json
import time
import asyncio
import logging
import argparse

import os
import websockets
from collections import deque

NUM_LINES = 1000
HEARTBEAT_INTERVAL = 15  # seconds

# init
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)

def process_line(log_line: str) -> dict:
    timestamp = log_line[0:20].strip()
    log_message = {
        'log_line': log_line,
        'timestamp': timestamp,
        'type': 'other'
    }
    if 'UpdateTip' in log_line:
        log_message['type'] = 'update_tip'
        data = log_line[34:]
        data = data.split()
        data = [d.split('=') for d in data]
        data[5][1] = data[5][1].replace("'", "") + ' ' + data.pop(6)[0].replace("'", "")
        log_message['data'] = dict(data)
    return json.dumps(log_message)


async def view_log(websocket, path):
    logging.info(
        'Connected, remote={}, path={}'.format(websocket.remote_address, path))
    try:
        with open(log_file) as f:
            log_lines = []
            for line in deque(f, NUM_LINES):
                log_lines.extend(line.split('\n'))
            log_lines = [l.strip() for l in log_lines if l.strip()]
            for log_line in log_lines:
                log_message = process_line(log_line)
                await websocket.send(log_message)

            last_heartbeat = time.time()
            while True:
                line = f.read()
                if not line.strip():
                    await asyncio.sleep(1)
                    if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
                        try:
                            await websocket.send('ping')
                            pong = await asyncio.wait_for(websocket.recv(), 5)
                            if pong != 'pong':
                                raise Exception()
                        except Exception:
                            raise Exception('Ping error')
                        else:
                            last_heartbeat = time.time()
                else:
                    lines = line.split('\n')
                    for log_line in lines:
                        log_message = process_line(log_line)
                        await websocket.send(log_message)




    except ValueError as e:
        try:
            await websocket.send(
                '<font color="red"><strong>{}</strong></font>'.format(e))
            await websocket.close()
        except Exception:
            pass

        log_close(websocket, path, e)

    except Exception as e:
        log_close(websocket, path, e)

    else:
        log_close(websocket, path)


def log_close(websocket, path, exception=None):
    message = 'Closed, remote={}, path={}'.format(websocket.remote_address,
                                                  path)
    if exception is not None:
        message += ', exception={}'.format(exception)
    logging.info(message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default=os.environ.get('WEBSOCKET_HOST', '127.0.0.1'))
    parser.add_argument('--port', type=int, default=os.environ.get('WEBSOCKET_PORT', 8765))
    parser.add_argument('--log', default='../../../docker/data/testnet3/debug.log')
    args = parser.parse_args()

    log_file = os.path.abspath(args.log)
    start_server = websockets.serve(view_log, args.host, args.port)
    print('connecting', args.host, args.port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
