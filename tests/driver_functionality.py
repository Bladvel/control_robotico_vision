from gpiozero import Motor
from time import sleep

# Definición de los motores según los pines
# Motor(left=IN1, right=IN2)

# OUT1 - OUT2 motor derecho
# OUT3 - OUT4 motor izquierdo

# Pin GPIO según la conexión física
# Motor derecho -> IN1: GPIO17, IN2: GPIO27
# Motor izquierdo -> IN3: GPIO5, IN4: GPIO6

motor_izquierdo = Motor(forward=5, backward=6)
motor_derecho = Motor(forward=17, backward=27)

# Funciones
def avanzar(velocidad=1.0):
    motor_izquierdo.forward(velocidad)
    motor_derecho.forward(velocidad)

def retroceder(velocidad=1.0):
    motor_izquierdo.backward(velocidad)
    motor_derecho.backward(velocidad)

def parar():
    motor_izquierdo.stop()
    motor_derecho.stop()

try:
    print("Avanzar...")
    avanzar(0.8)     # velocidad entre 0.0 y 1.0
    sleep(2)

    print("Retroceder...")
    retroceder(0.8)
    sleep(2)

    print("Parar")
    parar()

except KeyboardInterrupt:
    parar()
    print("\nPrograma interrumpido.")
