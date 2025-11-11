import cv2
import mediapipe as mp
import time
import os
import requests 
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.python.solutions import drawing_utils as mp_drawing
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.framework.formats import landmark_pb2

# --- 1. CONFIGURACIÓN DE RED ---
# ¡CAMBIA ESTA IP por la IP de tu Raspberry Pi!
IP_RASPBERRY_PI = "192.168.1.39"  # <-- (Ejemplo, usa la tuya)
URL_COMANDO_ROBOT = f"http://{IP_RASPBERRY_PI}:5000/comando"

# Variables para no "spamear" la red con comandos
ultimo_comando_enviado = None
tiempo_ultimo_comando = 0

def enviar_comando(accion, velocidad=0.3):
    """
    Envía un comando (ej: "AVANZAR") al servidor de la RPi.
    Optimizado para no enviar el mismo comando repetidamente.
    """
    global ultimo_comando_enviado, tiempo_ultimo_comando
    ahora = time.time()
    
    if accion != ultimo_comando_enviado or (ahora - tiempo_ultimo_comando > 1.0):
        try:
            print(f"Enviando comando: {accion}")
            requests.post(URL_COMANDO_ROBOT, 
                          json={'accion': accion, 'velocidad': velocidad}, 
                          timeout=0.5)
            
            ultimo_comando_enviado = accion
            tiempo_ultimo_comando = ahora
            
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al enviar {accion}: {e}")
            ultimo_comando_enviado = None 

# --- ¡NUEVA FUNCIÓN! TRADUCTOR DE LANDMARKS ---
def get_finger_states(hand_landmarks):
    """
    Analiza los landmarks de una mano y devuelve un diccionario
    con el estado (True=extendido, False=encogido) de los 4 dedos.
    Ignora el pulgar.
    """
    
    # Puntos de referencia: [Punta, Nudillo_Medio]
    # (Usamos el nudillo medio para más estabilidad)
    finger_points = {
        'index': [8, 6],
        'middle': [12, 10],
        'ring': [16, 14],
        'pinky': [20, 18]
    }
    
    states = {}
    
    try:
        # Comprobar si cada dedo está extendido (tip.y < joint.y)
        for finger, points in finger_points.items():
            tip_y = hand_landmarks[points[0]].y
            joint_y = hand_landmarks[points[1]].y
            
            # Si la punta del dedo está más ARRIBA (Y menor) que el nudillo,
            # el dedo está extendido.
            states[finger] = tip_y < joint_y
            
    except IndexError:
        # En caso de que un landmark no sea detectado
        return None

    return states
# --- FIN DE LA NUEVA FUNCIÓN ---

# --- 2. CONFIGURACIÓN DE MEDIAPIPE (Tu código) ---
model_path = 'hand_landmarker.task' #
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
    num_hands=1, # Optimizado para 1 mano (más rápido)
    min_hand_detection_confidence=0.5
)
detector = HandLandmarker.create_from_options(options)

# --- 3. CONFIGURACIÓN DE CÁMARA (Nuestros arreglos de WSL) ---
print("Abriendo cámara (WSL)...")
cap = cv2.VideoCapture('/dev/video0') 
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara en /dev/video0")
    exit()

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print("Cámara abierta. Presiona 'ESC' (tecla 27) para salir.")

# --- 4. BUCLE PRINCIPAL (CEREBRO + ENVÍO) ---
while cap.isOpened():
    ret, frame = cap.read()

    if not ret or frame is None:
        print("Frame corrupto o nulo, saltando...")
        time.sleep(0.03)
        continue
    
    # Voltear el frame horizontalmente (efecto espejo)
    # Esto hace que el control sea más intuitivo
    frame = cv2.flip(frame, 1)

    # --- Lógica de IA (como antes) ---
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)
    
    comando_actual = "PARAR" # Seguridad: por defecto, parar.

    # --- Lógica de Dibujo y Gestos ---
    if detection_result.hand_landmarks:
        # (Itera y dibuja la mano...)
        for hand_landmarks_list in detection_result.hand_landmarks:
            # (Código de dibujo)
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) 
                for landmark in hand_landmarks_list
            ])
            
            mp_drawing.draw_landmarks(
                frame, hand_landmarks_proto, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2)
            )

            # --- ! LÓGICA DE GESTOS MEJORADA ! ---
            
            # 1. Obtener el estado de los dedos de la mano detectada
            finger_states = get_finger_states(hand_landmarks_list) 
            
            if finger_states:
                # 2. Definir los gestos basados en los estados
                is_fist = (not finger_states['index'] and
                           not finger_states['middle'] and
                           not finger_states['ring'] and
                           not finger_states['pinky'])
                           
                is_index_up = (finger_states['index'] and
                               not finger_states['middle'] and
                               not finger_states['ring'] and
                               not finger_states['pinky'])
                               
                is_pinky_up = (not finger_states['index'] and
                               not finger_states['middle'] and
                               not finger_states['ring'] and
                               finger_states['pinky'])
                
                # 3. Decidir el comando
                if is_fist:
                    comando_actual = "PARAR"
                elif is_index_up:
                    comando_actual = "AVANZAR"
                elif is_pinky_up:
                    comando_actual = "RETROCEDER"
                # (Si no es ninguno, se queda como "PARAR")
            
            # --- Fin del Traductor de Gestos ---

    # Enviamos el comando decidido a la RPi
    enviar_comando(comando_actual)
    
    # Dibujar el comando en pantalla (para depurar)
    cv2.putText(frame, comando_actual, (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Mostrar el frame (como antes)
    cv2.imshow('Cerebro IA (WSL) - Presiona ESC para salir', frame)

    # Lógica de salida
    if cv2.waitKey(1) & 0xFF == 27: # 27 = Tecla ESC
        print("Saliendo... enviando comando PARAR final.")
        enviar_comando("PARAR")
        break

# --- 5. LIMPIEZA ---
cap.release()
cv2.destroyAllWindows()
print("Aplicación cerrada.")