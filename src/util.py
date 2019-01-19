import struct
import json

def serialize(msg):
    body = json.dumps(msg).encode()
    msg_len = struct.pack('>L', len(body))
    return msg_len + body


def deserialize(sock):
    _msg_len = sock.recv(4)
    if len(_msg_len) < 4:
        raise ConnectionResetError
    msg_len = struct.unpack('>L', _msg_len)[0]
    msg_raw = sock.recv(msg_len)
    while len(msg_raw) < msg_len:
        msg_raw += sock.recv(msg_len - len(msg_raw))
    msg = json.loads(msg_raw)
    return msg
