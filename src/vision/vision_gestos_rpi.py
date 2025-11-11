import cv2
import mediapipe as mp
import time
import os

# --- 1. Importaciones de MediaPipe (MISMAS) ---
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import hands as mp_hands

# --- 2. ¡NUEVA IMPORTACIÓN! ---
#    Esta es la librería para crear el objeto 'antiguo' que el dibujo necesita
from mediapipe.framework.formats import landmark_pb2

# --- 3. Recordatorio de variables de entorno para WSL ---
# export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0.0
# export QT_X11_NO_MITSHM=1

# --- 4. Configuración del Modelo (MISMO) ---
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print(f"Error: No se encuentra el modelo '{model_path}'.")
    exit()
    
BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.5
)
detector = HandLandmarker.create_from_options(options)

# --- 5. Configuración de Cámara (MISMO) ---
print("Abriendo cámara...")
url_del_stream = "http://192.168.1.8:8080"  # <-- ¡CAMBIA ESTA IP POR LA DE TU PC!
cap = cv2.VideoCapture(url_del_stream)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara en /dev/video0")
    exit()

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print("Cámara abierta. Presiona 'ESC' (tecla 27) para salir.")

# --- 6. Bucle Principal (Lógica Anti-Crash y NUEVO CÓDIGO DE DIBUJO) ---
while cap.isOpened():
    ret, frame = cap.read()

    if not ret or frame is None:
        print("Frame corrupto o nulo, saltando...")
        time.sleep(0.03)
    
    else:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        # --- ¡AQUÍ ESTÁ LA MAGIA! ---
        if detection_result.hand_landmarks:
            
            # 1. Iteramos sobre cada mano detectada
            #    (detection_result.hand_landmarks es una lista de listas: [[mano1_lmks], [mano2_lmks]])
            for hand_landmarks_list in detection_result.hand_landmarks:
                
                # 2. Creamos el objeto 'NormalizedLandmarkList' vacío que 'draw_landmarks' espera
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                
                # 3. Llenamos ese objeto con los datos de nuestra lista 'nueva'
                hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) 
                    for landmark in hand_landmarks_list
                ])
                
                # 4. ¡Ahora sí llamamos a draw_landmarks con el objeto correcto!
                mp_drawing.draw_landmarks(
                    frame,                 
                    hand_landmarks_proto,  # <-- Le pasamos el objeto 'antiguo'
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2)
                )
        # --- FIN DEL CÓDIGO NUEVO ---

        cv2.imshow('MediaPipe Hands (Presiona ESC para salir)', frame)

    if cv2.waitKey(1) & 0xFF == 27: # 27 = Tecla ESC
        print("Saliendo...")
        break

# --- 7. Limpieza (MISMO) ---
cap.release()
cv2.destroyAllWindows()