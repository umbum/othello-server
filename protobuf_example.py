#! /usr/bin/env python

import othello_pb2
import sys

try:
  raw_input          # Python 2
except NameError:
  raw_input = input  # Python 3


if len(sys.argv) != 2:
  print("Usage:", sys.argv[0], "SAVE_FILE")
  sys.exit(-1)

msg = othello_pb2.ServerMsg()
msg.type = 2
msg.turn.time_limit = 50
msg.turn.opponent_decision = 61
msg.turn.changed_points.extend([15, 33])
msg.turn.available_points.extend([32, 12])
msg.turn.opponent_status = 0

# Write the new address book back to disk.
with open(sys.argv[1], "wb") as f:
  length = f.write(msg.SerializeToString())

recv_msg = othello_pb2.ServerMsg()  
with open(sys.argv[1], "rb") as f:
  recv_msg.ParseFromString(f.read(length))

print(recv_msg.type)
print(recv_msg.turn)
