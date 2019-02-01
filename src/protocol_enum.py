from enum import IntEnum

class MsgType(IntEnum):
  READY    = 0
  START    = 1
  TURN     = 2
  ACCEPT   = 3
  TIMEOUT  = 4    # not used
  NOPOINT  = 5
  GAMEOVER = 6
  ERROR    = 7
  FULL     = 8

class OpponentStatus(IntEnum):
  NORMAL  = 0
  TIMEOUT = 1    # not used
  NOPOINT = 2

class GameoverReason(IntEnum):
  # --- normal ---
  # condition 1. board가 꽉 참.
  # condition 2. 한 종류의 돌이 전멸. 이 경우 내가 놓으면서 내가 질 수는 없으니까, 상대방 색상 돌이 있는지만 체크하면 된다.
  # condition 3. 양측 모두 NOPOINT.
  # --- abnormal ---
  # condition 4. timeout
  # condition 5. error
  BOARD_FULL   = 0
  ANNIHILATION = 1
  BOTH_NOPOINT = 2
  TIMEOUT      = 3
  ERROR        = 4


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