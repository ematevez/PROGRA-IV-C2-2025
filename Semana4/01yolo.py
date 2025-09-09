# pip install opencv-python opencv-contrib-python numpy ultralytics
# https://www.youtube.com/@OMES-va
# https://www.youtube.com/watch?v=Cgxsv1riJhI


# import cv2
# import numpy as np

# # Cargar YOLO
# net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
# with open("coco.names", "r") as f:
#     classes = [line.strip() for line in f.readlines()]

# layer_names = net.getLayerNames()
# output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# cap = cv2.VideoCapture(0)

# while True:
#     ret, frame = cap.read()
#     height, width, _ = frame.shape

#     # Crear blob para YOLO
#     blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), swapRB=True, crop=False)
#     net.setInput(blob)
#     outs = net.forward(output_layers)

#     for out in outs:
#         for detection in out:
#             scores = detection[5:]
#             class_id = np.argmax(scores)
#             confidence = scores[class_id]
#             if confidence > 0.5:
#                 # Coordenadas de detección
#                 x, y, w, h = (detection[0:4] * [width, height, width, height]).astype("int")
#                 cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#                 cv2.putText(frame, classes[class_id], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

#     cv2.imshow("YOLO Detection", frame)

#     if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
#         break

# cap.release()
# cv2.destroyAllWindows()

from ultralytics import YOLO
import cv2

# Cargar modelo YOLO pre-entrenado (COCO dataset)
model = YOLO("yolov8n.pt")  # "n" = nano (más rápido)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results = model(frame, stream=True)  # detección en vivo

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            conf = box.conf[0]
            cls = int(box.cls[0])
            label = model.names[cls]
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    cv2.imshow("YOLOv8 Detection", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
