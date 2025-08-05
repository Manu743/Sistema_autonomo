import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject,QUrl
import traceback

def excepthook(type, value, tback):
    print("Error detectado:")
    traceback.print_exception(type, value, tback)

sys.excepthook = excepthook

class MapBridge(QObject):
    # Señal para emitir la ubicación seleccionada
    locationSelected = pyqtSignal(float, float)

    @pyqtSlot(float, float)
    def emitLocation(self, lat, lng):
        
        self.locationSelected.emit(lat,lng)

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa Interactivo")
        self.setGeometry(100, 100, 800, 600)

        # Crear el puente para interactuar con el mapa
        self.bridge = MapBridge()
        self.bridge.locationSelected.connect(self.onLocationSelected)

        # Crear un área de mapa usando QWebEngineView
        self.map_view = QWebEngineView()
        self.map_view.loadFinished.connect(self.injectBridge)
        self.map_view.load(QUrl("file:///C:/Users/maren/OneDrive/Desktop/Proyecto/Diseño/Menu/mapa.html"))
        # Crear y configurar el canal para conectar JavaScript con Python
        self.channel = QWebChannel()
        self.channel.registerObject("pyqt", self.bridge)
        self.map_view.page().setWebChannel(self.channel)
        # Configurar el diseño de la ventana
        layout = QVBoxLayout()
        layout.addWidget(self.map_view)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def injectBridge(self):
        if not hasattr(self, "channel_initialized"):
            self.channel_initialized = True  # Marca el canal como inicializado
            self.map_view.page().setWebChannel(self.channel)

    def onLocationSelected(self, lat, lng):
        print(f"Ubicación recibida en Python: Latitud {lat}, Longitud {lng}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())
