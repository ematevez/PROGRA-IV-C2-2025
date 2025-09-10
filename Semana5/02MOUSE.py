# pip install mediapipe pyautogui opencv-python

# import cv2
# import mediapipe as mp
# import pyautogui

# cap = cv2.VideoCapture(0)
# hand_detector = mp.solutions.hands.Hands()
# drawing = mp.solutions.drawing_utils

# screen_w, screen_h = pyautogui.size()

# while True:
#     ret, frame = cap.read()
#     frame = cv2.flip(frame, 1)
#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = hand_detector.process(rgb)

#     if results.multi_hand_landmarks:
#         for hand in results.multi_hand_landmarks:
#             drawing.draw_landmarks(frame, hand)

#             # Índice
#             x = int(hand.landmark[8].x * screen_w)
#             y = int(hand.landmark[8].y * screen_h)
#             pyautogui.moveTo(x, y)

#     cv2.imshow("Hand Mouse", frame)
#     if cv2.waitKey(1) & 0xFF == 27:  # ESC
#         break

# cap.release()
# cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import pyautogui
import math

cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands()
drawing = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            drawing.draw_landmarks(frame, hand)

            # Coordenadas índice (landmark 8)
            ix = int(hand.landmark[8].x * screen_w)
            iy = int(hand.landmark[8].y * screen_h)

            # Coordenadas pulgar (landmark 4)
            px = int(hand.landmark[4].x * screen_w)
            py = int(hand.landmark[4].y * screen_h)

            # Mover mouse al índice
            pyautogui.moveTo(ix, iy)

            # Distancia entre índice y pulgar
            dist = math.hypot(px - ix, py - iy)

            if dist < 40:  # umbral (ajustar según cámara)
                pyautogui.click()
                cv2.putText(frame, "CLICK", (ix, iy-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.imshow("Hand Mouse", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()



#!=============================================================

#?=============================================================


#=============================================================


#TODO=============================================================