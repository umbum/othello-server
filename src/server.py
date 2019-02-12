import logging
import socket
import threading
import time

import numpy as np

import log
import processing
from protocol_enum import *
from util import *

HOST = ''
PORT = 8472
logger = logging.getLogger("othello")

# accept하는 main thread 1개랑, room이라는 thread 1개. 채팅같은거나 내 턴이 아닐 때의 user interaction을 생각하면 user마다 thread를 만들어서 recv해야 하는게 맞긴 한데.. 빠르게 구현하려면 그냥 room으로 thread 잡는게 편할 듯.

class Room(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.black = None
        self.white = None
        self.turn_user = None
        self.wait_user = None
        self.TIME_LIMIT = 30    # 판당 30초?로 하기로 했던가??
        self.BOARD_SIZE = 8
        self.board = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.prev_nopoint = False

    def run(self):
        try:
            self.threadMain()
        except ConnectionRefusedError as e:
            # client 측에 뭔가 오류가 있는 경우.
            logger.error(str(e))
            pass
        except ConnectionResetError as e:
            # client가 종료한 경우
            logger.error(str(e))
            pass
        except ConnectionAbortedError as e:
            logger.error("send하려고 하는데 User.sock이 닫힌 경우.")
        # except Exception as e:
            # logger.error(exc_info=e)
        finally:
            # 다시 게임할 수 있도록 clear하는 작업을.
            time.sleep(10)
            self.turn_user.sock.close()
            self.wait_user.sock.close()
            self.__init__()
            logger.info("----clear & reset----")


    def threadMain(self):
        """
        종료는 5가지 경우.
        --- normal ---
        condition 1. board가 꽉 참.
        condition 2. 한 종류의 돌이 전멸. 이 경우 내가 놓으면서 내가 질 수는 없으니까, 상대방 색상 돌이 있는지만 체크하면 된다.
        condition 3. 양측 모두 NOPOINT.
        --- abnormal ---
        condition 4. timeout
        condition 5. error
        """
        logger.debug("start Room thread")
        self.initBoard()

        self.turn_user = self.black    # 흑부터 시작
        self.wait_user = self.white

        self.turn_user.sock.settimeout(self.TIME_LIMIT)
        self.wait_user.sock.settimeout(self.TIME_LIMIT)

        winner = None
        loser  = None

        prev_put_point = None
        prev_changed_point = None
        prev_opponent_status = OpponentStatus.NORMAL
        gameover_reason = None

        self.white.send({
            "type": MsgType.START,
            "color": Color.WHITE
        })
        self.black.send({
            "type": MsgType.START,
            "color": Color.BLACK
        })

        while True:
            available_points = self.processAvailablePoints(self.turn_user.color)
            if len(available_points) == 0:
                # NOPOINT
                if prev_opponent_status == OpponentStatus.NOPOINT:
                    # condition 3. 양측 모두 NOPOINT
                    # 승 패는 계산해봐야 알 수 있음.
                    gameover_reason = GameoverReason.BOTH_NOPOINT
                    winner, loser = self.checkWinner()
                    break
                else:
                    self.turn_user.send({
                        "type": MsgType.NOPOINT,
                        "opponent_put": prev_put_point,
                        "changed_points": prev_changed_point
                    })
                    prev_put_point = None
                    prev_changed_point = None
                    prev_opponent_status = OpponentStatus.NOPOINT
                    self.turn_user, self.wait_user = self.wait_user, self.turn_user
                    continue

            self.turn_user.send({
                "type": MsgType.TURN,
                "time_limit": self.TIME_LIMIT,
                "available_points": available_points,
                "opponent_put": prev_put_point,
                "changed_points": prev_changed_point,
                "opponent_status": prev_opponent_status
            })
            prev_opponent_status = OpponentStatus.NORMAL
            
            try:
                msg = self.turn_user.recv()
            except (socket.timeout, TimeoutError):
                # condition 4. Timeout
                logger.debug("timeout!")
                prev_put_point = None
                prev_changed_point = None
                gameover_reason = GameoverReason.TIMEOUT
                # wait_user가 win. turn_user가 lose
                winner, loser = self.wait_user, self.turn_user
                break
            
            logger.debug(msg)
            
            validation_msg = self.validateInput(msg, available_points)
            if validation_msg is not True:
                # condition 5. error
                self.turn_user.send({
                    "type": MsgType.ERROR,
                    "msg": validation_msg
                })
                logger.error(validation_msg)

                gameover_reason = GameoverReason.ERROR
                # wait_user가 win. turn_user가 lose
                winner, loser = self.wait_user, self.turn_user
                break

            self.turn_user.send({
                "type": MsgType.ACCEPT,
                "opponent_time_limit": self.TIME_LIMIT
            })
            prev_put_point = msg["point"]
            prev_changed_point = self.updateBoard(msg["point"])
            print(self.board)

            gameover_reason = self.checkGameover()
            if gameover_reason is not None:
                # condition 1, 2.
                if gameover_reason == GameoverReason.BOARD_FULL:
                    # condition 1인 경우 승/패는 계산해봐야 알 수 있음.
                    winner, loser = self.checkWinner()
                elif gameover_reason == GameoverReason.ANNIHILATION:
                    # condition 2인 경우 turn_user가 win, wait_user가 lose.
                    winner, loser = self.turn_user, self.wait_user
                break

            self.turn_user, self.wait_user = self.wait_user, self.turn_user
        # while end

        assert(gameover_reason is not None)

        if winner == self.turn_user:
            turn_user_result = Result.WIN
            wait_user_result = Result.LOSE
            winner_color = "BLACK" if self.turn_user.color == Color.BLACK else "WHITE"
        elif winner == self.wait_user:
            turn_user_result = Result.LOSE
            wait_user_result = Result.WIN
            winner_color = "BLACK" if self.wait_user.color == Color.BLACK else "WHITE"
        else:
            turn_user_result = Result.DRAW
            wait_user_result = Result.DRAW
            winner_color = "DRAW"

        self.turn_user.send({
            "type": MsgType.GAMEOVER,
            "reason": gameover_reason,
            "result": turn_user_result,
        })
        self.wait_user.send({
            "type": MsgType.GAMEOVER,
            "reason": gameover_reason,
            "result": wait_user_result,
            "opponent_put": prev_put_point,
            "changed_points": prev_changed_point
        })

        logger.info("[GAMEOVER] reason: {} | result: {}".format(gameover_reason, winner_color))


    def validateInput(self, msg, available_points):
        if (msg.get("type") != ClntType.PUT):
            return "message type is not PUT"
        elif (msg.get("point") is None):
            return "message field 'point' is None"
        
        i, j= msg["point"]
        if (i, j) not in available_points:
            return "abusing? point is not in avaliable_points"
        
        return True

    def updateBoard(self, point):
        # TURN 보낼 때 available_points 계산하면서 놓으면 뒤집히는 애들까지 같이 저장해놓고. 놓았을 때 그거 불러와서 뒤집어버리면 더 효율적이긴 한데. 그냥 만든거 쓰자.
        i, j = point
        point_to_reverse = processing.getReversedPosition(self.board, self.turn_user.color, i, j)
        self.board[i][j] = self.turn_user.color
        for i, j in point_to_reverse:
            self.board[i][j] = self.turn_user.color
        return point_to_reverse
            
    def processAvailablePoints(self, color):
        """
        색상이 color인 player가 놓을 수 있는 곳의 좌표를 계산
        thanks to SeongBin!

        Returns
        -------
        List<Tuple<int>>
        """
        return processing.getAvailablePosition(self.board, color)

    def checkGameover(self):
        if np.count_nonzero(self.board) == self.BOARD_SIZE * self.BOARD_SIZE:
            # condition 1. board full
            return GameoverReason.BOARD_FULL
        elif len(np.where(self.board == self.wait_user.color)[0]) == 0:
            # condition 2. 한 종류의 돌이 전멸. 이 경우 내가 놓으면서 내가 질 수는 없으니까, 상대방 색상 돌이 있는지만 체크하면 된다.
            return GameoverReason.ANNIHILATION

        return None

    
    def checkWinner(self):
        num_black = np.count_nonzero(self.board == Color.BLACK)
        num_white = np.count_nonzero(self.board == Color.WHITE)
        if num_black > num_white:
            return self.black, self.white
        elif num_black < num_white:
            return self.white, self.black
        else:        
            # DRAW
            return None, None


    def initBoard(self):
        self.board[3][3] = Color.WHITE
        self.board[3][4] = Color.BLACK
        self.board[4][3] = Color.BLACK
        self.board[4][4] = Color.WHITE


class User:
    def __init__(self, sock, color):
        self.sock = sock
        self.color = color

    def send(self, msg):
        return self.sock.sendall((serialize(msg)))
    
    def recv(self):
        return deserialize(self.sock)


class AcceptServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))
        self.sock.settimeout(1)

    def run(self):
        logger.debug("start AcceptServer")
        self.sock.listen(1)
        while True:
            try:
                try:
                    clnt_sock, _ = self.sock.accept()
                except socket.timeout:
                    continue
            except KeyboardInterrupt:
                break
            
            if room.black is None:
                # set black player
                room.black = User(clnt_sock, Color.BLACK)
                # send READY
                room.black.send({
                    "type": MsgType.READY
                })
                print("[JOIN] P1 (BLACK)")
            elif room.white is None:
                # set white player
                print("[JOIN] P2 (WHITE)")
                room.white = User(clnt_sock, Color.WHITE)
                room.start()
            else:
                clnt_sock.send(serialize({
                    "type": MsgType.FULL
                }))
                clnt_sock.close()
        
        self.sock.close()

# 한 타임에 한 게임만 진행하도록 구성할 것이므로, room 1개만.
room = Room()
if __name__ == "__main__":
    server = AcceptServer()
    server.run()
