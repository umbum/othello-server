

## 서버-클라이언트 모델

공정한 게임을 위해서는 믿을 수 있는 서버의 중재가 필요하다. MORPG처럼 플레이에 참여하는 호스트들 끼리만 별도로 연결해서 플레이하도록 하면 메인 서버의 부하를 줄일 수 있지만, 어뷰징을 막기 어렵다. 한 게임씩 진행할 것이므로 P2P보단 서버-클라이언트 모델로 구성하여 어뷰징을 막는다.(기본적으로 클라이언트를 신뢰하지 않는 구조.)

또한, 서버-클라이언트 모델은 나중에 프로세싱 이슈가 생겨 서버 측 기보 계산 로직을 들어낸다고 하더라도 큰 문제가 생기지 않는다. Abuse 검증 로직만 빠지게 되는 것이기 때문이다.

반면 P2P는 나중에 검증 로직을 넣고 싶어도 모든 구조를 수정하지 않으면 로직을 넣을 수 없다.



#### 서버

대부분의 로직이 여기서 처리된다.

서버의 역할은 다음과 같음.



#### 클라이언트

- GUI 인터페이스 제공
- 놓을 위치를 선택하고 서버에게 전송
- 서버에서 받은 데이터를 렌더링



## protocol

서버와 클라이언트가 교환하는 패킷은 4byte length와 이 길이 만큼의 message로 구성된다. 

| 4byte length | nbyte message |
| ------ | ------- |

message는 정해진 key-value로 이루어진 json 형식의 데이터로 한다.

#### message format : json

- pickle은 python native해서 python에서 쓰기는 편리하지만, 타 언어에서 파싱하기 부자연스럽고 별도의 서드 파티 라이브러리를 사용해야 한다는 단점이 있다.
- protobuf는 schema를 나타내기 좋고, binary 기반이라 compact하고 빠르다. 정해진 schema대로 serialize/deserialize할 수 있어서 구현 안정성이 높아 보인다. 그러나 모든 구성원들이 protobuf 사용법을 익혀야 한다는 단점이 있다.
- json은 human readable하며, 보편적으로 많이 쓰는 포맷으로 친숙하고 serialization/deserialization을 간단히 처리할 수 있는 신뢰할 수 있는 API가 제공된다는 장점이 있다. 그러나 text 기반이라 조금 느리고 약간의 추가적인 overhead가 있다.

이 경우 주고받는 데이터의 양이 크지 않고, 대부분의 딜레이는 클라이언트 측에서 다음 수를 결정하는데에서 올 것이기 때문에 데이터의 양이나 속도 등 json의 단점보다 보편성, 편의성에서 오는 장점이 크다고 생각해 json으로 결정하게 되었다.

#### Server -> Client로 보내는 메시지 타입

- READY
- START
- TURN
- ACCEPT
- TIMEOUT
- NOPOINT
- GAMEOVER
- ERROR



#### Client->Server로 보내는 메시지 타입

- ClntDecision



## 기타

- packet logging
