"""
Author : SeongBin Hong
Special thanks to SeongBin!
"""
import numpy as np
from protocol_enum import *


def chkArrow(map,color,x,y,direction):  # x,y 좌표로부터 direction방향까지 뒤집힐 수 있는 돌을 반환하는 함수
    result = []
    while True:
        x += direction[0]     #direction 방향으로 이동
        y += direction[1]
        if not ((0 <= x <= 7) and (0 <= y <= 7)): # 맵 바운더리 체크
            break
        nowPositionColor = map[x][y]   # 해당 위치에 있는 돌을 가져옴
        if nowPositionColor == 0:   # 공백이면 반환 x
            break
        if nowPositionColor == color:   # 내 돌 색깔이면 리스트 리턴  
            return result
        result.append((x, y))     # 상대 돌 색깔이면 리스트에 삽입
    return []

def getReversedPosition(map,color,x,y):
    direction = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]   # 8개의 방향
    result = []
    for dir in direction:   # 모든 방향으로 탐색
        tmpList = chkArrow(map,color,x,y,dir)   # 해당 방향에 뒤집을 돌 리스트
        if tmpList:  # 뒤집을 돌 있냐?
            result += tmpList  # 리스트 추가
    return result  # 뒤집을 수 있는 돌 모두 리턴

def chkAround(map, x,y,color):   # 돌 주변 8칸에 나랑 다른 색의 돌이 있는지 체크하는 함수. 만들었는데 쓸모 없어서 쓰진 않음.
    direction = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    for dir in direction:
        if not ((0 <= x+dir[0] <= 7) or (0 <= y+dir[1] <= 7)):  # 바운더리 체크
            break
        if map[x+dir[0]][y+dir[1]] not in [0, color]: # 상대방 돌이 존재하면 True 리턴
            return True
    return False   # 다 찾아봤는데 상대방 돌이 주변에 없으면 False 리턴

def getAvailablePosition(board, color):
    result = []
    for i, j in zip(*np.where(board == 0)):
        if getReversedPosition(board,color,i,j):  # 해당 좌표가 비어있고, 해당 방향에서 뒤집을 수 있는 돌 리스트가 비어있지 않으면
            result.append((int(i),int(j)))  #좌표 기입
    return result  # 착수 가능한 좌표 리스트 반환


def test():
    board = np.zeros((8,8), dtype=int)
    board[3][3] = Color.BLACK
    board[3][4] = Color.WHITE
    board[4][3] = Color.WHITE
    board[4][4] = Color.BLACK
    board[4][2] = Color.WHITE
    print(board)
    print(getAvailablePosition(board, Color.BLACK))
    print(getReversedPosition(board, Color.BLACK, 4, 1))

if __name__ == "__main__":
    test()