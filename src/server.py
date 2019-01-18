import socket
import threading
from util import *
from protocol_enum import *
import numpy as np
import processing

HOST = ''
PORT = 8472

# 한 타임에 한 게임만 진행하도록 구성할 것이므로, room 1개만.
room = Room()

# accept하는 main thread 1개랑, room이라는 thread 1개. 채팅같은거나 내 턴이 아닐 때의 user interaction을 생각하면 user마다 thread를 만들어서 recv해야 하는게 맞긴 한데.. 빠르게 구현하려면 그냥 room으로 thread 잡는게 편할 듯.

class Room(threading.Thread):
    def __init__(self):
        self.black = None
        self.white = None
        self.turn_user = None
        self.wait_user = None
        self.TIME_LIMIT = 30    # 판당 30초?로 하기로 했던가??
        self.BOARD_SIZE = 8
        self.board = np.zeros((self.BOARD_SIZE, self.BOARD_SIZE), dtype=int)
        self.prev_nopoint = False

    def run(self):
        if self.white is None or self.black is None:
            raise ValueError("white or black user isn't set")
        self.initBoard()
        self.white.send({
            "type": MsgType.START
            "color": Color.WHITE
        })
        self.black.send({
            "type": MsgType.START
            "color": Color.BLACK
        })
        
        self.turn_user = self.black    # 흑부터 시작
        self.wait_user = self.white
        while True:
            available_points = self.processAvailablePoints(self.turn_user.color)
            if len(available_points) == 0:
                self.turn_user.send({
                    "type": MsgType.NOPOINT,
                    "opponent_put": [3, 7],
                    "changed_points": [[0, 3], [7, 0]]
                })
                prev_nopoint = True
                continue

            self.turn_user.send({
                "type": MsgType.TURN,
                "time_limit": self.TIME_LIMIT,
                "opponent_put": None,
                "changed_points": None,
                "available_points": available_points
            })
            prev_nopoint = False
            
            try:
                msg = self.turn_user.recv()
            except ConnectionResetError as e:
                print("error")
                break
            except TimeoutError as e:
                # 패배처리 하기로 했지. setsockopt로 timeout 설정하는것도 추가해야하고.
                pass
            
            print(msg)
            
            validation_msg = self.validateInput(msg, available_points)
            if validation_msg is not True:
                self.turn_user.send({
                    "type": MsgType.ERROR,
                    "msg": validation_msg
                })
                self.wait_user.send({
                    "type": MsgType.GAMEOVER
                })
                print("validation FAIL")
                break

            self.turn_user.send({
                "type": MsgType.ACCEPT,
                "opponent_time_limit": self.TIME_LIMIT
            })
            point = desimalToPoint(msg["point"])
            self.updateBoard(point)
            self.checkGameover()


    def validateInput(self, msg, available_points):
        if (msg.get("type") != "PUT"):
            return "message type is not PUT"
        elif (msg.get("point") is None):
            return "message field 'point' is None"
        
        point = decimalToPoint(msg["point"])
        if point not in available_points:
            return "abusing? point is not in avaliable_points"
        
        return True

    def updateBoard(self, point):
        # TURN 보낼 때 available_points 계산하면서 놓으면 뒤집히는 애들까지 같이 저장해놓고. 놓았을 때 그거 불러와서 뒤집어버리면 더 효율적이긴 한데. 그냥 만든거 쓰자.
        i, j = point
        point_to_reverse = processing.getReversedPosition(self.board, self.turn_user.color, i, j)
        self.board[i][j] = self.turn_user.color
        for i, j in point_to_reverse:
            self.board[i][j] = self.turn_user.color
            

    def processAvailablePoints(self, color):
        """
        색상이 color인 player가 놓을 수 있는 곳의 좌표를 계산
        thanks to SeongBin!

        Returns
        -------
        List<Tuple<int>>
        """
        return processing.getAvailablePosition(self.board, self.turn_user.color)

    def checkGameover(self):
        # condition 1. board가 꽉 참.
        # condition 2. 한 종류의 돌이 전멸. 이 경우 내가 놓으면서 내가 질 수는 없으니까, 상대방 색상 돌이 있는지만 체크하면 된다.
        # condition 3. 양측 모두 NOPOINT.
        
        if np.count_nonzero(self.board) == self.BOARD_SIZE * self.BOARD_SIZE:
            # board full
            return "full"
        elif len(np.where(self.board == self.wait_user.color)[0]) == 0:
            # 상대방 돌 전멸
            return "annihilation"
        elif

        return False


    def initBoard(self):
        self.board[3][3] = Color.BLACK
        self.board[3][4] = Color.WHITE
        self.board[4][3] = Color.WHITE
        self.board[4][4] = Color.BLACK


class User:
    def __init__(self, sock, color):
        self.sock = sock
        self.color = color

    def send(self, msg):
        return self.sock(serialize(msg))
    
    def recv(self):
        _msg_len = self.sock.recv(4)
        if len(_msg_len) < 4:
            raise ConnectionResetError
        msg_len = struct.unpack('>L', _msg_len)[0]
        msg_raw = self.sock.recv(msg_len)
        while len(msg_raw) < msg_len:
            msg_raw += self.sock.recv(msg_len - len(msg_raw))
        msg = json.loads(msg_raw)
        return msg


class AcceptServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((HOST, PORT))

    def run(self):
        self.sock.listen(1)
        while True:
            clnt_sock, _ = self.sock.accept()
            if room.black is None:
                # set black player
                room.black = User(clnt_sock, Color.BLACK)
                # send READY
                room.black.send({
                    "type": MsgType.READY
                })
            elif room.white is None:
                # set white player
                room.white = User(clnt_sock, Color.WHITE)
                room.start()
            else:
                clnt_sock.send(serialize({
                    "type": MsgType.FULL
                }))
                clnt_sock.close()
            

if __name__ == "__main__":
    server = AcceptServer()
    server.run()