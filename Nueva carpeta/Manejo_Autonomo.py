import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import torch
import pathlib
import cv2
import numpy as np
import requests
import websockets
import asyncio

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')



temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

model = torch.hub.load('ultralytics/yolov5',
                       'custom',
                       path='C:/1/bestn.pt',
                       force_reload=False,
                       source='github')

print("Inferencia en:", next(model.model.parameters()).device)

url = 'http://192.168.1.105/'

ws = "ws://192.168.1.100:81"

async def enviar_ws(comando):
    try:
        async with websockets.connect(ws) as websocket:
            await websocket.send(comando)
            print(f"[ws] Enviado: {comando}")
    except Exception as e:
        print(f"[ws] Error al enviar comando {e}")

def enviar(comando):
    asyncio.run(enviar_ws(comando))

def activar(nombre):
    print(f"alerta {nombre} detectado")

while True:
    response = requests.get(url)
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_tensor = torch.from_numpy(img_rgb).permute(2,0,1).to(device).float()/255.0

    alto, ancho = frame.shape[:2]
    w_zona, h_zona = 100, 100
    cx, cy = ancho // 2, alto // 2

    zona_frontal = (cx - w_zona // 2, cy - h_zona // 2, cx + w_zona // 2, cy + h_zona // 2)
    zona_izquierda = (0, cy - h_zona // 2, cx - w_zona // 2, cy + h_zona // 2)
    zona_derecha = (cx + w_zona // 2, cy - h_zona // 2, ancho, cy + h_zona // 2)


    detect = model(frame)
    info = detect.pandas().xyxy[0]

    obstaculo_frontal = False
    obstaculo_izq = False
    obstaculo_der = False

    for i in range(len(info)):
        x1, y1, x2, y2 = int(info.iloc[i]['xmin']), int(info.iloc[i]['ymin']), int(info.iloc[i]['xmax']), int(info.iloc[i]['ymax'])
        nombre = info.iloc[i]['name']

        centro_x = int((x1 + x2) / 2)
        centro_y = int((y1 + y2) / 2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, nombre, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        cv2.circle(frame, (centro_x, centro_y), 5, (0, 0, 255), -1)

        zx1, zy1, zx2, zy2 = zona_frontal
        if zx1 <= centro_x <= zx2 and zy1 <= centro_y <= zy2:
            obstaculo_frontal = True
            activar(nombre)

        zx1, zy1, zx2, zy2 = zona_izquierda
        if zx1 <= centro_x <= zx2 and zy1 <= centro_y <= zy2:
            obstaculo_izq = True

        zx1, zy1, zx2, zy2 = zona_derecha
        if zx1 <= centro_x <= zx2 and zy1 <= centro_y <= zy2:
            obstaculo_der = True

    # Dibujar zonas
    cv2.rectangle(frame, (zona_izquierda[0], zona_izquierda[1]), (zona_izquierda[2], zona_izquierda[3]), (0,255,255), 1)
    cv2.rectangle(frame, (zona_derecha[0], zona_derecha[1]), (zona_derecha[2], zona_derecha[3]), (0,255,255), 1)
    cv2.rectangle(frame, (zona_frontal[0], zona_frontal[1]), (zona_frontal[2], zona_frontal[3]), (255,0,0), 2)

    # Decisión de evasión

    if obstaculo_frontal:
        if not obstaculo_der:
            print("derecha")
            #enviar("derecha")
        elif not obstaculo_izq:
            print("izquierda")
            #enviar("izquierda")
        else:
            print("detener")
            #enviar("detener")
    else:
        print("adelante")
        #enviar("adelante")

    cv2.imshow('Detector', np.squeeze(detect.render()))
    t = cv2.waitKey(5)
    if t == 27:
        break

cv2.destroyAllWindows()
