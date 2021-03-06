import socket
from util import *
from protocol_enum import *
from enum import IntEnum
import time
import random

HOST = '127.0.0.1'
PORT = 8472


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sock.settimeout(1)
    while True:
        try:
            msg = deserialize(sock)
        except socket.timeout:
            continue
        print(msg)
        time.sleep(0.1)
        if msg["type"] == MsgType.TURN:
            available_points = msg["available_points"]
            
            sock.sendall(serialize({
                "type": ClntType.PUT,
                "point": random.choice(available_points)
            }))
        elif msg["type"] == MsgType.GAMEOVER:
            break
    print("GAME OVER!")
    sock.close()