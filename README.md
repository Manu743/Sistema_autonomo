# Sistema Autónomo

Estación de control para robots móviles autónomos con navegación en grilla, detección de obstáculos y generación de reportes.

## Arquitectura

```
Sistema_autonomo/
├── GUI Login/          # Pantalla de autenticación
│   └── Loguin.py       # Login con SHA-256 + SQLite
├── Menu/               # Dashboard principal
│   ├── Menu.py         # CRUD de robots, áreas, usuarios, mapas, reportes
│   ├── bd.py           # Capa de base de datos SQLite
│   ├── Clases.py       # DTOs (Robots, Usuarios, Areas, Matriz)
│   ├── PDF.py          # Visor de reportes PDF
│   └── mapa.html       # Mapa interactivo Leaflet.js
├── Control/            # Módulo de control del robot
│   └── Control.py      # Video streaming, YOLOv5, ArUco, WebSocket, grilla
├── Nueva carpeta/      # Prototipos y firmware Arduino
│   └── websocket/websocket.ino  # ESP32 WebSocket server
└── datos.db            # Base de datos SQLite local (no versionada)
```

## Requisitos

- Python 3.11
- Cámara web (para vista aérea)
- ESP32-CAM (cámara del robot)
- Robot con ESP32 y WebSocket en puerto 881
- Modelo YOLOv5 personalizado (`bestn.pt` en `C:/1/`)
- Archivo de calibración (`calibracion_camera.npz`)

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Base de datos

`datos.db` no se versiona porque contiene datos personales y hashes de contraseñas.
Para crear la base local con el usuario administrador inicial:

```bash
set SEED_ADMIN_PASSWORD=tu-contrasena
python "./Menu/init_db.py"
```

El firmware de `Nueva carpeta/websocket` lee las credenciales de red desde
`secrets.h`, que tampoco se versiona: copiar `secrets.example.h` a `secrets.h`
y completar los valores.

## Uso

```bash
python "./GUI Login/Loguin.py"
```

## Funcionalidades

- **Autenticación**: Login con contraseñas hasheadas (SHA-256) y roles
- **CRUD**: Gestión de robots, áreas, usuarios
- **Mapa interactivo**: Selección de coordenadas vía Leaflet.js (OpenStreetMap)
- **Video streaming**: Cámara aérea webcam + ESP32-CAM en tiempo real
- **Navegación autónoma**: Recorrido serpentina en grilla 5×5 con ArUco
- **Detección de obstáculos**: YOLOv5 en feed de ESP32-CAM
- **Detección de minas**: Sensor ESP32
- **Reportes PDF**: Matriz de recorrido superpuesta en imagen satelital

## Stack

- **GUI**: PyQt5 + QtWebEngine
- **Visión**: OpenCV, ArUco, YOLOv5 (PyTorch)
- **Comunicación**: WebSocket (robot), HTTP MJPEG (ESP32-CAM)
- **BD**: SQLite
- **PDF**: ReportLab + PyMuPDF
- **Firmware**: Arduino (ESP32)
