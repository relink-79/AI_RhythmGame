import cv2
import mediapipe as mp
import random
import time

# 화면 크기 설정 (실행환경에서의 캠코더 해상도입니다)
WIDTH, HEIGHT = 640, 480

# MediaPipe 손 객체 생성, 그리기 코드 불러오기
model = mp.solutions.hands
hand = model.Hands()
drawinghands = mp.solutions.drawing_utils

# 노드 클래스
class Note:
    # 노드 처음 x좌표, y좌표, 낙하속도, 판정여부, 경과시간
    def __init__(self, x, y, speed, drop_time):
        self.x = x
        self.y = y
        self.speed = speed
        self.judged = False
        self.drop_time = drop_time

    # 노드 이동(y 좌표를 spped 만큼)
    def update(self):
        self.y += self.speed

    def draw(self, frame):
        cv2.rectangle(frame, (self.x, self.y), (self.x + 100, self.y + 20), (135, 206, 250), -1)  # 노트를 그리기

#노드 저장, 속도, 오차시간, y좌표 등등 필요한 변수를 선언하는것
notes = []
speed = 10
judgment = ""
timingerror = 0
jtime = 0
jliney = 442
score = 0
zoneflags = [False, False, False, False]
ignore = [0, 0, 0, 0]
lasttime = 0

# 판정값 중앙 좌표
positions = [30, 190, 350, 510]


def Pandan(frame, judgment, timingerror):
    # 판단 후 judgement 변수를 어떤 글꼴, 두께, 좌표에 둘 것인지 계산 후 출력
    textsize1 = cv2.getTextSize(judgment, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
    # text size의 x y좌표 계산 (중앙에 위치하도록 하게)
    textx1 = (WIDTH - textsize1[0]) // 2
    texty1 = (HEIGHT + textsize1[1]) // 2
    cv2.putText(frame, judgment, (textx1, texty1), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

    #error 출력 화면
    errortext = f"{timingerror} ms"
    errorsize1 = cv2.getTextSize(errortext, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    errorx1 = (WIDTH - errorsize1[0]) // 2
    errory1 = texty1 + textsize1[1] + 10
    cv2.putText(frame, errortext, (errorx1, errory1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

# score 표시
def comgogaesan(frame, score):
    cv2.putText(frame, f"score: {score}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

#노드를 렌덤 위치에 떨어트리는 코드
def note_mandulgi():
    x = random.choice(positions)
    return Note(x, 0, speed, random.randint(1200, 1800))

# CV2 화면에 생기는 박스 및 판정선 그리기
def draw_zones(frame):
    zoneh = 150
    for i in range(4):
        cv2.rectangle(frame, (i * 160, HEIGHT - zoneh), ((i + 1) * 160, HEIGHT), (0, 255, 0), 2)
        cv2.line(frame, (i * 160, HEIGHT - zoneh + 3 * zoneh // 4),
                 ((i + 1) * 160, HEIGHT - zoneh + 3 * zoneh // 4), (0, 0, 0), 2)

# 손가락 인식 영역을 그리기
def songurigi(frame, x, y):
    cv2.rectangle(frame, (x - 20, y - 32), (x + 20, y + 32), (255, 0, 0), 2)

# 카메라 화면 출력
cap = cv2.VideoCapture(0)



while True:
    # cv2 카메라 Frame 읽어오는 함수, 실패하면 break 탈출
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임을 640x480으로 리사이즈
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    # 좌우반전(실행 환경에서 좌우반전이 필요했습니다.)
    frame = cv2.flip(frame, 1)
    # RGB로 변환 후 mediapipe 사용
    results = hand.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    # 시간을 밀리초로 저장
    now = int(time.time() * 1000)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 검지 끝의 x,y좌표를 계산 후 그리기 함수 출력하여 그리기
            x = int(hand_landmarks.landmark[model.HandLandmark.INDEX_FINGER_TIP].x * WIDTH)
            y = int(hand_landmarks.landmark[model.HandLandmark.INDEX_FINGER_TIP].y * HEIGHT)
            songurigi(frame, x, y)
            #4개의 판정영역을 반복하며 확인함
            for i in range(4):
                # 판정 범위에 손가락이 들어왔고, 다음 노드와 500ms 차이인지 확인
                if (i * 160 - 20) <= x < ((i + 1) * 160 + 20) and (jliney - 50) <= y < (jliney + 50):
                    # 판정영역이 손가락이 처음 들어왔는지, 500ms가 지났는지
                    if not zoneflags[i] and now > ignore[i]:
                        #손가락이 있고, 500ms동안 판정을 내리지 않게 함.
                        zoneflags[i] = True
                        ignore[i] = now + 500
                        closest_note = None
                        #작은 거리를 저장, 초기값
                        mindistance = float('inf')
                        # 노드 for문
                        for note in notes:
                            #같은 좌표(X좌표)에 있는지, 아직 판정되지 않은지 확인
                            if note.x == positions[i] and not note.judged:
                                # 거리 계산
                                distance = abs(jliney - (note.y + 20))
                                # 작은거리 바꾸기, 가장 가까운 노드를설정
                                if distance < mindistance:
                                    mindistance = distance
                                    closest_note = note
                        # 노드의 y, 판정라인 y좌표의 거라 사이 범위를 확인 후 판정 진행
                        if closest_note:
                            if jliney - 100 <= closest_note.y + 20 <= jliney + 100:
                                judgment = "BAD"
                            if jliney - 50 <= closest_note.y + 20 <= jliney + 50:
                                judgment = "GOOD"
                                score += 50
                            if jliney - 20 <= closest_note.y + 20 <= jliney + 20:
                                judgment = "PERFECT"
                                score += 100
                            if judgment == "MISS":
                                judgment = "MISS"
                                
                            # 오차 계산(10단위)
                            timingerror = (abs(mindistance) // 10) * 10 
                            # 가까운 노드 판정 완료, 리스트에서 제거 후 ms 설정
                            closest_note.judged = True
                            notes.remove(closest_note)
                            jtime = int(time.time() * 1000)
                # 리스트 False로 반환
                else:
                    zoneflags[i] = False

    for note in notes:
        # node 이동
        note.update()
        # 노드가 화면에서 벗어난다면 MISS, 노드제거
        if note.y > HEIGHT:
            notes.remove(note)
            judgment = "MISS"
            timingerror = 100
            jtime = int(time.time() * 1000)

    # 노드가 떨어진 시간을 계산, 일정 시간이 지났거나
    if len(notes) == 0 or (notes and int(time.time() * 1000) - lasttime > notes[-1].drop_time):
        notes.append(note_mandulgi())  # 새로운 노트를 추가
        lasttime = int(time.time() * 1000)
        
    # 모든 노드에 그리기
    for note in notes:
        note.draw(frame) 

    #마지막 판정과의 차이 구하기, 결과 표시
    if judgment and int(time.time() * 1000) - jtime < 1000:
        Pandan(frame, judgment, timingerror)

    #점수 계산 및 출력
    comgogaesan(frame, score)
    draw_zones(frame)
    cv2.imshow("Rhythme game", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
