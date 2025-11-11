import os
import time
import cv2

DEVICE = '/dev/video0'
has_display = bool(os.environ.get('DISPLAY'))

# Prefer V4L2 backend
cap = cv2.VideoCapture(DEVICE, cv2.CAP_V4L2)

if not cap.isOpened():
    print(f"Error: No se pudo abrir la cámara en {DEVICE}")
    raise SystemExit(1)

# Try safer uncompressed first, then MJPG
def try_fourcc(code: str) -> bool:
    ok = cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*code))
    got = int(cap.get(cv2.CAP_PROP_FOURCC))
    cur = "".join([chr((got >> 8*i) & 0xFF) for i in range(4)])
    return ok and cur == code

for fourcc in ('MJPG','YUYV'):
    if try_fourcc(fourcc):
        print(f"FOURCC configurado: {fourcc}")
        break

# Set conservative resolution and FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Cámara abierta {w}x{h} @ {fps:.1f} FPS. Presiona 'q' para salir.")

window_name = 'Prueba de Cámara'
if has_display:
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

frame_count = 0
try:
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Frame corrupto o nulo, saltando...")
            time.sleep(0.005)
            continue

        if has_display:
            try:
                cv2.imshow(window_name, frame)
                # Break if window was closed by WM
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    print("Ventana cerrada. Saliendo...")
                    break
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Saliendo...")
                    break
            except cv2.error as e:
                print(f"Error de GUI/X11: {e}. Cambiando a modo headless.")
                has_display = False
        else:
            # Headless: print status occasionally
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"OK frames: {frame_count} - tamaño {frame.shape}")
            time.sleep(0.005)
finally:
    cap.release()
    if has_display:
        cv2.destroyAllWindows()