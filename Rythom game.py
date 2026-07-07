import cv2
import mediapipe as mp
import random
import time

WIDTH, HEIGHT = 640, 480

model = mp.solutions.hands
hand = model.Hands()
drawinghands = mp.solutions.drawing_utils

class Note:
    def __init__(self, x, y, speed, drop_time):
        self.x = x
        self.y = y
        self.speed = speed
        self.judged = False
        self.drop_time = drop_time

    def update(self):
        self.y += self.speed

    def draw(self, frame):
        cv2.rectangle(frame, (self.x, self.y), (self.x + 100, self.y + 20), (135, 206, 250), -1)  # 노트를 그리기

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

positions = [30, 190, 350, 510]


def Pandan(frame, judgment, timingerror):
    textsize1 = cv2.getTextSize(judgment, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
    textx1 = (WIDTH - textsize1[0]) // 2
    texty1 = (HEIGHT + textsize1[1]) // 2
    cv2.putText(frame, judgment, (textx1, texty1), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)

    errortext = f"{timingerror} ms"
    errorsize1 = cv2.getTextSize(errortext, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    errorx1 = (WIDTH - errorsize1[0]) // 2
    errory1 = texty1 + textsize1[1] + 10
    cv2.putText(frame, errortext, (errorx1, errory1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def comgogaesan(frame, score):
    cv2.putText(frame, f"score: {score}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def note_mandulgi():
    x = random.choice(positions)
    return Note(x, 0, speed, random.randint(1200, 1800))

def draw_zones(frame):
    zoneh = 150
    for i in range(4):
        cv2.rectangle(frame, (i * 160, HEIGHT - zoneh), ((i + 1) * 160, HEIGHT), (0, 255, 0), 2)
        cv2.line(frame, (i * 160, HEIGHT - zoneh + 3 * zoneh // 4),
                 ((i + 1) * 160, HEIGHT - zoneh + 3 * zoneh // 4), (0, 0, 0), 2)

def songurigi(frame, x, y):
    cv2.rectangle(frame, (x - 20, y - 32), (x + 20, y + 32), (255, 0, 0), 2)

cap = cv2.VideoCapture(0)



while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.flip(frame, 1)
    results = hand.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    now = int(time.time() * 1000)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x = int(hand_landmarks.landmark[model.HandLandmark.INDEX_FINGER_TIP].x * WIDTH)
            y = int(hand_landmarks.landmark[model.HandLandmark.INDEX_FINGER_TIP].y * HEIGHT)
            songurigi(frame, x, y)
            for i in range(4):
                if (i * 160 - 20) <= x < ((i + 1) * 160 + 20) and (jliney - 50) <= y < (jliney + 50):
                    if not zoneflags[i] and now > ignore[i]:
                        zoneflags[i] = True
                        ignore[i] = now + 500
                        closest_note = None
                        mindistance = float('inf')
                        for note in notes:
                            if note.x == positions[i] and not note.judged:
                                distance = abs(jliney - (note.y + 20))
                                if distance < mindistance:
                                    mindistance = distance
                                    closest_note = note
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
                                
                            timingerror = (abs(mindistance) // 10) * 10 
                            closest_note.judged = True
                            notes.remove(closest_note)
                            jtime = int(time.time() * 1000)
                else:
                    zoneflags[i] = False

    for note in notes:
        note.update()
        if note.y > HEIGHT:
            notes.remove(note)
            judgment = "MISS"
            timingerror = 100
            jtime = int(time.time() * 1000)

    if len(notes) == 0 or (notes and int(time.time() * 1000) - lasttime > notes[-1].drop_time):
        notes.append(note_mandulgi())  # 새로운 노트를 추가
        lasttime = int(time.time() * 1000)
        
    for note in notes:
        note.draw(frame) 

    if judgment and int(time.time() * 1000) - jtime < 1000:
        Pandan(frame, judgment, timingerror)

    comgogaesan(frame, score)
    draw_zones(frame)
    cv2.imshow("Rhythme game", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
