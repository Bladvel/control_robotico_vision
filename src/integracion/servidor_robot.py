from flask import Flask, request, jsonify
import time

# --- IMPORTACIÓN DE MOTORES ---
# Importamos tus funciones de motor desde la carpeta 'tests'
# según la estructura de tu repositorio
try:
    # (Tu script usa gpiozero por dentro)
    from src.control.driver_functionality import avanzar, retroceder, parar
    print("Módulos de motor (gpiozero) cargados exitosamente.")
except ImportError as e:
    print(f"ADVERTENCIA: No se pudieron cargar los motores: {e}")
    print("El servidor funcionará, pero imprimirá simulaciones.")
    # Creamos funciones falsas (dummies) para que el servidor no falle
    def avanzar(velocidad=1.0): print(f"Simulando AVANZAR a velocidad {velocidad}")
    def retroceder(velocidad=1.0): print(f"Simulando RETROCEDER a velocidad {velocidad}")
    def parar(): print("Simulando PARAR")

# --- CONFIGURACIÓN DEL SERVIDOR ---
app = Flask(__name__)

# Mapeo de comandos (string) a funciones (código)
# Por seguridad, solo permitimos los comandos de esta lista
comandos_validos = {
    "AVANZAR": avanzar,
    "RETROCEDER": retroceder,
    "PARAR": parar,
    # Puedes añadir más aquí (ej. "GIRAR_IZQ": girar_izquierda)
    # pero primero defínelos en 'driver_functionality.py'
}

# Esta es la "ruta" o "endpoint" que tu PC/WSL llamará
@app.route('/comando', methods=['POST'])
def manejar_comando():
    data = request.json
    accion = data.get('accion') # ej: "AVANZAR"
    velocidad = data.get('velocidad', 0.3) # Velocidad opcional, default 0.8
    
    print(f"Comando recibido: {accion} @ {velocidad}")

    if accion in comandos_validos:
        try:
            # Si el comando es válido, ejecuta la función asociada
            funcion_motor = comandos_validos[accion]
            
            if accion == "PARAR":
                funcion_motor() # Llama a parar()
            else:
                funcion_motor(velocidad) # Llama a avanzar(velocidad)
                
            return jsonify(status="OK", accion_ejecutada=accion)
        
        except Exception as e:
            print(f"Error ejecutando motor: {e}")
            return jsonify(status="Error", mensaje=f"Error interno del motor: {e}"), 500
    else:
        # Si el comando no está en nuestro diccionario
        return jsonify(status="Error", mensaje="Comando no reconocido"), 400

# --- Punto de entrada ---
if __name__ == '__main__':
    print("===============================================")
    print("Iniciando servidor de control del robot (Flask)...")
    print("Escuchando comandos en http://0.0.0.0:5000/comando")
    print("===============================================")
    # 'host=0.0.0.0' hace que el servidor sea visible en tu red local
    app.run(host='0.0.0.0', port=5000, debug=False)