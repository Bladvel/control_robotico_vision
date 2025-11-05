# control_robotico_vision

Proyecto de control robótico con visión por computadora utilizando MediaPipe, OpenCV y procesamiento de audio.

## 📋 Requisitos

- Python 3.8 o superior
- (Opcional) WSL2 si estás en Windows

## 🖥️ Instalación de WSL2 en Windows

Si estás usando Windows, se recomienda usar WSL2 (Windows Subsystem for Linux) para mejor compatibilidad con las librerías de visión.

### Pasos para instalar WSL2:

1. **Abrir PowerShell como Administrador** y ejecutar:
   ```powershell
   wsl --install
   ```

2. **Reiniciar el equipo** cuando se solicite.

3. **Configurar usuario y contraseña** de Ubuntu al iniciar por primera vez.

4. **Actualizar WSL** (opcional pero recomendado):
   ```powershell
   wsl --update
   ```

5. **Verificar la versión de WSL**:
   ```powershell
   wsl --list --verbose
   ```
   Debe mostrar versión 2.

6. **Instalar una distribución específica** (si no se instaló automáticamente):
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

### Acceder a WSL2:
- Desde el menú inicio, buscar "Ubuntu" o "WSL"
- Desde PowerShell/CMD: `wsl`
- Desde Windows Terminal: agregar perfil de Ubuntu

## 🚀 Instalación del Proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/Bladvel/control_robotico_vision.git
cd control_robotico_vision
```

### 2. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/WSL/Mac
# venv\Scripts\activate   # En Windows (CMD/PowerShell sin WSL)
```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. (Opcional) Instalar dependencias del sistema para OpenCV
Si tienes problemas con OpenCV en Linux/WSL:
```bash
sudo apt update
sudo apt install -y python3-opencv libopencv-dev
sudo apt install -y libportaudio2  # Para sounddevice
```

## 📂 Estructura del Proyecto

```
control_robotico_vision/
├── src/
│   ├── vision/        # Módulos de visión por computadora
│   ├── control/       # Módulos de control robótico
│   └── integracion/   # Integración de componentes
├── docs/
│   ├── informe_uai.docx
│   └── referencias/
├── tests/             # Pruebas unitarias
├── media/             # Recursos multimedia
├── requirements.txt   # Dependencias del proyecto
└── README.md
```

## ▶️ Ejecución del Proyecto

### Activar el entorno virtual
```bash
source venv/bin/activate  # Linux/WSL/Mac
# venv\Scripts\activate   # Windows sin WSL
```

### Ejecutar módulos
```bash
# Ejemplo: ejecutar módulo de visión
python3 src/vision/main.py

# Ejemplo: ejecutar módulo de control
python3 src/control/main.py

# Ejemplo: ejecutar integración completa
python3 src/integracion/main.py
```

## 🛠️ Desarrollo

### Agregar nuevas dependencias
```bash
pip install nueva-libreria
pip freeze > requirements.txt
```

### Ejecutar tests
```bash
python3 -m pytest tests/
```

## 📦 Dependencias Principales

- **opencv-python**: Procesamiento de imágenes y video
- **mediapipe**: Detección de poses y gestos
- **numpy**: Operaciones numéricas
- **matplotlib**: Visualización de datos
- **scipy**: Algoritmos científicos
- **sounddevice**: Captura y reproducción de audio

## 🐛 Solución de Problemas

### Error con sounddevice en WSL
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install --upgrade sounddevice
```

### Error con OpenCV y GUI en WSL
Para usar ventanas gráficas en WSL2, instalar un servidor X:
```bash
# Instalar VcXsrv en Windows
# En WSL, configurar DISPLAY
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

### Problemas con MediaPipe
Asegúrate de usar Python 3.8-3.11 (MediaPipe puede tener problemas con versiones más nuevas):
```bash
python3 --version
```

## 👥 Contribuidores

- [Bladvel](https://github.com/Bladvel)

## 📄 Licencia

Este proyecto es parte de un trabajo académico de la UAI.
