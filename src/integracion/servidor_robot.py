from flask import Flask, request, jsonify
import time

try:
    from src.control.driver_functionality import avanzar, retroceder, parar
    print("Módulos de motor (gpiozero) cargados exitosamente.")
except ImportError as e:
    print(f"ADVERTENCIA: No se pudieron cargar los motores: {e}")
    print("El servidor funcionará, pero imprimirá simulaciones.")
    # Creamos funciones falsas (dummies) para que el servidor no falle
    def avanzar(velocidad=1.0): print(f"Simulando AVANZAR a velocidad {velocidad}")
    def retroceder(velocidad=1.0): print(f"Simulando RETROCEDER a velocidad {velocidad}")
    def parar(): print("Simulando PARAR")


app = Flask(__name__)

# Mapeo de comandos (string) a funciones (código)
comandos_validos = {
    "AVANZAR": avanzar,
    "RETROCEDER": retroceder,
    "PARAR": parar,
}

@app.route('/comando', methods=['POST'])
def manejar_comando():
    data = request.json
    accion = data.get('accion')
    velocidad = data.get('velocidad', 0.3) 
    
    print(f"Comando recibido: {accion} @ {velocidad}")

    if accion in comandos_validos:
        try:
            funcion_motor = comandos_validos[accion]
            
            if accion == "PARAR":
                funcion_motor() 
            else:
                funcion_motor(velocidad)
                
            return jsonify(status="OK", accion_ejecutada=accion)
        
        except Exception as e:
            print(f"Error ejecutando motor: {e}")
            return jsonify(status="Error", mensaje=f"Error interno del motor: {e}"), 500
    else:
        return jsonify(status="Error", mensaje="Comando no reconocido"), 400

if __name__ == '__main__':
    print("===============================================")
    print("Iniciando servidor de control del robot (Flask)...")
    print("Escuchando comandos en http://0.0.0.0:5000/comando")
    print("===============================================")
    app.run(host='0.0.0.0', port=5000, debug=False)