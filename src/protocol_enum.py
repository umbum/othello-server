from enum import IntEnum

class MsgType(IntEnum):
  READY    = 0
  START    = 1
  TURN     = 2
  ACCEPT   = 3
  TIMEOUT  = 4
  NOPOINT  = 5
  GAMEOVER = 6
  ERROR    = 7
  FULL     = 8

class OpponentStatus(IntEnum):
  NORMAL  = 0
  TIMEOUT = 1
  NOPOINT = 2

class Color(IntEnum):
  EMPTY = 0
  BLACK = 1
  WHITE = 2

class Result(IntEnum):
  LOSE = 0
  WIN  = 1
  DRAW = 2


class ClntType(IntEnum):
  PUT = 0