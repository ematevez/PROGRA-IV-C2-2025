import pygame
import random
import sys
import cv2
import mediapipe as mp
import numpy as np
import time

# ==== CONFIG MEDIAPIPE ====
mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
last_blink_time = 0
double_blink_delay = 0.5

def euclidean_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def eye_aspect_ratio(eye_landmarks):
    v1 = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    v2 = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
    h = euclidean_distance(eye_landmarks[0], eye_landmarks[3])
    return (v1 + v2) / (2.0 * h)

# ==== CONFIG PYGAME ====
pygame.init()
ANCHO, ALTO = 640, 480
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego controlado con cabeza y ojos 👁️")

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (200, 0, 0)
VERDE = (0, 200, 0)

# Jugador
jugador = pygame.Rect(50, ALTO//2, 40, 40)

# Balas y enemigos
balas = []
enemigos = []
vel_bala = 7
vel_enemigo = 3

# Eventos
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1500)

# Vidas y puntaje
vidas = 3
puntos = 0
fuente = pygame.font.SysFont(None, 36)

def disparar(x, y):
    bala = pygame.Rect(x + 40, y + 15, 10, 5)
    balas.append(bala)

def crear_enemigo():
    y = random.randint(0, ALTO - 40)
    enemigo = pygame.Rect(ANCHO - 40, y, 40, 40)
    enemigos.append(enemigo)

# ==== BUCLE PRINCIPAL ====
reloj = pygame.time.Clock()

while True:
    # ----- CAPTURA CAMARA -----
    ret, frame = cap.read()
    if not ret:
        break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    h, w, _ = frame.shape

    disparo = False

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            lm = face_landmarks.landmark

            # Nariz → mover jugador
            nose = (int(lm[1].x * w), int(lm[1].y * h))
            jugador.x = int((nose[0] / w) * ANCHO)
            jugador.y = int((nose[1] / h) * ALTO)

            # Dibujar nariz
            cv2.circle(frame, nose, 4, (0, 0, 255), -1)

            # Detectar parpadeo
            right_eye_idx = [33, 160, 158, 133, 153, 144]
            left_eye_idx = [362, 385, 387, 263, 373, 380]

            right_eye = [(int(lm[i].x * w), int(lm[i].y * h)) for i in right_eye_idx]
            left_eye = [(int(lm[i].x * w), int(lm[i].y * h)) for i in left_eye_idx]

            # Dibujar ojos
            for (x, y) in right_eye + left_eye:
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

            ear_right = eye_aspect_ratio(right_eye)
            ear_left = eye_aspect_ratio(left_eye)
            ear = (ear_right + ear_left) / 2.0

            if ear < 0.22:
                if time.time() - last_blink_time < double_blink_delay:
                    disparo = True
                last_blink_time = time.time()

    # ----- EVENTOS PYGAME -----
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            cap.release()
            cv2.destroyAllWindows()
            pygame.quit()
            sys.exit()
        if evento.type == SPAWN_EVENT:
            crear_enemigo()

    # ----- DISPARO -----
    if disparo:
        disparar(jugador.x, jugador.y)

    # Mover balas
    for bala in balas[:]:
        bala.x += vel_bala
        if bala.x > ANCHO:
            balas.remove(bala)

    # Mover enemigos
    for enemigo in enemigos[:]:
        enemigo.x -= vel_enemigo
        if enemigo.x < 0:
            enemigos.remove(enemigo)

    # Colisiones
    for bala in balas[:]:
        for enemigo in enemigos[:]:
            if bala.colliderect(enemigo):
                balas.remove(bala)
                enemigos.remove(enemigo)
                puntos += 10
                break

    for enemigo in enemigos[:]:
        if jugador.colliderect(enemigo):
            enemigos.remove(enemigo)
            vidas -= 1
            if vidas <= 0:
                print("GAME OVER")
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()

    # ----- DIBUJAR JUEGO -----
    ventana.fill(NEGRO)
    pygame.draw.rect(ventana, VERDE, jugador)
    for bala in balas:
        pygame.draw.rect(ventana, BLANCO, bala)
    for enemigo in enemigos:
        pygame.draw.rect(ventana, ROJO, enemigo)

    # HUD
    texto = fuente.render(f"Vidas: {vidas}   Puntos: {puntos}", True, BLANCO)
    ventana.blit(texto, (10, 10))

    pygame.display.flip()
    reloj.tick(30)

    # ----- MOSTRAR CAMARA -----
    cv2.imshow("Camara - Seguimiento Facial", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
        cap.release()
        cv2.destroyAllWindows()
        pygame.quit()
        sys.exit()
