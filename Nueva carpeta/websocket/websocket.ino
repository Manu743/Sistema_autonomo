#include <WiFi.h>
#include <WebSocketsServer.h>

// Credenciales de red: se definen en secrets.h, fuera del repositorio.
// Copiar secrets.example.h como secrets.h y completar los valores.
#include "secrets.h"

// Puerto WebSocket (ej. 81)
WebSocketsServer webSocket = WebSocketsServer(81);

void setup() {
  Serial.begin(115200);

  // Conectar a WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a WiFi...");
  }

  Serial.print("IP del ESP32: ");
  Serial.println(WiFi.localIP());

  // Iniciar servidor WebSocket
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  webSocket.loop();
}

// Función para manejar eventos del WebSocket
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.printf("[%u] Desconectado!\n", num);
      break;
    case WStype_CONNECTED:
      Serial.printf("[%u] Conectado desde la IP: %s\n", num, webSocket.remoteIP(num).toString().c_str());
      break;
    case WStype_TEXT:
      // Recibir mensaje desde el cliente
      Serial.printf("[%u] Mensaje recibido: %s\n", num, payload);
      
      // Ejemplo: Enviar confirmación al cliente
      String respuesta = "ESP32 recibió: " + String((char*)payload);
      webSocket.sendTXT(num, respuesta);
      break;
  }
}