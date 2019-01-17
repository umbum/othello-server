

## 서버-클라이언트 모델

공정한 게임을 위해서는 믿을 수 있는 서버의 중재가 필요하다. MORPG처럼 플레이에 참여하는 호스트들 끼리만 별도로 연결해서 플레이하도록 하면 메인 서버의 부하를 줄일 수 있지만, 어뷰징을 막기 어렵다. 한 게임씩 진행할 것이므로 P2P보단 서버-클라이언트 모델로 구성하여 어뷰징을 막는다.

\* 기본적으로 클라이언트를 신뢰하지 않는 구조.



또한, 서버-클라이언트 모델은 나중에 프로세싱 이슈가 생겨 서버 측 기보 계산 로직을 들어낸다고 하더라도 큰 문제가 생기지 않는다. Abuse 검증 로직만 빠지게 되는 것이기 때문이다.

반면 P2P는 나중에 검증 로직을 넣고 싶어도 모든 구조를 수정하지 않으면 로직을 넣을 수 없다.



#### 서버

- 대부분의 로직을  처리
- player 설정
- input validation
- processing
     - no available point check
- timeout check
- gameover check
- turn 분배



#### 클라이언트

- GUI 인터페이스 제공
- 놓을 위치 결정
- 서버에서 받은 데이터를 렌더링



## protocol

서버와 클라이언트가 교환하는 패킷은 4byte length와 이 길이 만큼의 message로 구성된다. 

| 4byte length | nbyte message |
| ------ | ------- |

message는 정해진 key-value로 이루어진 json 형식의 데이터로 한다.

예제
```
b'\x0b\x00\x00\x00{"type": 8}'
```

### message format : json

- pickle은 python native해서 python에서 쓰기는 편리하지만, 타 언어에서 파싱하기 부자연스럽고 별도의 서드 파티 라이브러리를 사용해야 한다는 단점이 있다.
- protobuf는 schema를 나타내기 좋고, binary 기반이라 compact하고 빠르다. 정해진 schema대로 serialize/deserialize할 수 있어서 구현 안정성이 높아 보인다. 그러나 모든 구성원들이 protobuf 사용법을 익혀야 한다는 단점이 있다.
- json은 human readable하며, 보편적으로 많이 쓰는 포맷으로 친숙하고 serialization/deserialization을 간단히 처리할 수 있는 신뢰할 수 있는 API가 제공된다는 장점이 있다. 그러나 text 기반이라 조금 느리고 약간의 추가적인 overhead가 있다.

이 경우 주고받는 데이터의 양이 크지 않고, 대부분의 딜레이는 클라이언트 측에서 다음 수를 결정하는데에서 올 것이기 때문에 데이터의 양이나 속도 등 json의 단점보다 보편성, 편의성에서 오는 장점이 크다고 생각해 json으로 결정하게 되었다.



### Server -> Client로 보내는 메시지 타입

- READY
- START
- TURN
- ACCEPT
- TIMEOUT
- NOPOINT
- GAMEOVER
- ERROR



#### READY

상대방 플레이어를 대기하고 있을 때 수신



#### START

게임 시작 시 양측 수신

`init_state :InitState` 초기 돌 위치 설정

`color :Color` 흑/백 플레이어 설정(먼저 들어가면 자동으로 흑)



#### TURN

턴이 넘어올 때 수신

`time_limit :uint32`  나의 턴일 때, 시간 제한

`opponent_put :uint32`  상대방이 놓은 마지막 수의 좌표.

`changed_points :List<uint32>` 상대방이 놓은 마지막 수로 인해 뒤집힌 돌의 좌표(서버 측 프로세싱 결과)

`available_points :List<uint32>` 현재 턴에 놓을 수 있는 좌표

`opponent_status: OpponentStatus` 이전 턴 상대방의 상태(e.g., timeout)



#### ACCEPT

클라이언트 턴 종료 시 수신

`opponent_time_limit :uint32` 상대방 턴일 때, 상대방의 시간 제한



#### TIMEOUT

타임아웃 시 게임 종료



#### NOPOINT

돌을 놓을 곳이 없을 때 수신

`opponent_put :uint32`  상대방이 놓은 마지막 수의 좌표.

`changed_points :List<uint32>` 상대방이 놓은 마지막 수로 인해 뒤집힌 돌의 좌표(서버 측 프로세싱 결과)

`opponent_status: OpponentStatus` 이전 턴 상대방의 상태(e.g., timeout)



#### GAMEOVER

게임이 종료되었을 때 수신

`result :Result` 게임 결과

`opponent_put :uint32`  상대방이 놓은 마지막 수의 좌표.

`changed_points :List<uint32>` 상대방이 놓은 마지막 수로 인해 뒤집힌 돌의 좌표(서버 측 프로세싱 결과)



#### ERROR

abusing이나 서버 오류 시 수신

`msg :string` 오류 메시지



### Client->Server로 보내는 메시지 타입

#### PUT

`point :uint32` 놓은 돌의 좌표



### 돌의 좌표

```
opponent_put, changed_points, available_points, point
```

돌의 위치는 8*8 오델로를 2차원 배열로 관리할 것을 고려하여 10진수 정수 00~77을 사용하도록 한다.

십의 자리는 행, 일의 자리는 열을 나타낸다.

-------------------
key-value 정보는 [sample.json](https://github.com/umbum/othello-with-RL/blob/master/sample.json) 참고. (자료형 및 상세 정보는 [othello.proto](https://github.com/umbum/othello-with-RL/blob/master/othello.proto) 참고.)

sequence는 [SequanceDiagram.mdj](https://github.com/umbum/othello-with-RL/blob/master/SequenceDiagram.mdj)  참고. (starUML)





## 기타

- packet logging
