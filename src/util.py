import struct
import json

def serialize(msg):
    body = json.dumps(msg).encode()
    msg_len = struct.pack('<L', len(body))
    return msg_len + body

def decimalToPoint(decimal):
    j = decimal % 10
    i = int((decimal - j) / 10)
    return (i, j)
