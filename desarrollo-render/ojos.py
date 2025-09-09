import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Inicializar FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Config cámara
cap = cv2.VideoCapture(0)

# Dimensiones de pantalla
screen_w, screen_h = pyautogui.size()

# Variables de click
last_blink_time = 0
double_blink_delay = 0.5

# Función para distancia
def euclidean_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# EAR para parpadeo
def eye_aspect_ratio(eye_landmarks):
    vertical1 = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    vertical2 = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
    horizontal = euclidean_distance(eye_landmarks[0], eye_landmarks[3])
    return (vertical1 + vertical2) / (2.0 * horizontal)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    h, w, _ = frame.shape

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Usamos algunos puntos clave de la cara
            landmarks = face_landmarks.landmark

            # Coordenadas de nariz (centro de referencia)
            nose = (int(landmarks[1].x * w), int(landmarks[1].y * h))

            # Mapear movimiento de nariz a pantalla
            mouse_x = screen_w - int((nose[0] / w) * screen_w)
            mouse_y = int((nose[1] / h) * screen_h)
            pyautogui.moveTo(mouse_x, mouse_y, duration=0.05)

            # Dibujar nariz
            cv2.circle(frame, nose, 3, (0, 0, 255), -1)

            # Detectar parpadeo con EAR
            right_eye_indices = [33, 160, 158, 133, 153, 144]
            left_eye_indices = [362, 385, 387, 263, 373, 380]

            right_eye = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in right_eye_indices]
            left_eye = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in left_eye_indices]

            ear_right = eye_aspect_ratio(right_eye)
            ear_left = eye_aspect_ratio(left_eye)
            ear = (ear_right + ear_left) / 2.0

            # Dibujar ojos
            for (x, y) in right_eye + left_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            if ear < 0.22:  # ojo cerrado
                if time.time() - last_blink_time < double_blink_delay:
                    pyautogui.click()
                    print("👁️ Doble parpadeo → CLICK")
                last_blink_time = time.time()

    cv2.imshow("Head Mouse Control", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
        break

cap.release()
cv2.destroyAllWindows()
