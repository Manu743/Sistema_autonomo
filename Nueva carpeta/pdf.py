import sys, os
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QScrollArea,
    QVBoxLayout, QWidget, QPushButton, QFileDialog, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage 
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generar_reporte(datos, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    elementos = []
    estilos = getSampleStyleSheet()

    # Título
    elementos.append(Paragraph(f"Reporte de {datos['nombre']}", estilos['Title']))
    elementos.append(Spacer(1, 12))

    # Datos principales
    elementos.append(Paragraph(f"Capacidad: {datos['capacidad']}", estilos['Normal']))
    elementos.append(Paragraph(f"Tiempos: {datos['tiempos']}", estilos['Normal']))
    elementos.append(Spacer(1, 12))

    # Matriz como tabla
    if "matriz" in datos:
        tabla = Table(datos["matriz"])
        elementos.append(tabla)
        elementos.append(Spacer(1, 12))

    # Imagen
    if "imagen" in datos and os.path.exists(datos["imagen"]):
        elementos.append(Image(datos["imagen"], width=200, height=150))
        elementos.append(Spacer(1, 12))

    doc.build(elementos)

class ReportePDFWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista del reporte en PDF")
        self.resize(800, 600)

        fecha_str = datetime.now().strftime("%d_%m_%Y_%I%M%p")
        self.pdf_path = f'./reporte_{fecha_str}.pdf'

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # Área de scroll para visualizar el PDF
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        # Contenedor de páginas
        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.vbox = QVBoxLayout(self.container)

        # Info de paginación
        self.lbl_paginas = QLabel("Hojas: 0")
        self.lbl_paginas.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_paginas)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar como...")
        self.btn_guardar.clicked.connect(self.guardar_como)
        btn_layout.addWidget(self.btn_guardar)
        self.layout.addLayout(btn_layout)

        # Datos de prueba
        datos = {
            "nombre": 'Manuel',
            "capacidad": '2',
            "tiempos": '01:00 PM',
            "matriz": [[1,2,3],[4,5,6],[7,8,9]],
            "imagen": './Menu/Imagenes/1.png'
        }
        
        generar_reporte(datos, self.pdf_path)
        self.mostrar_pdf()

    def mostrar_pdf(self):
        doc = fitz.open(self.pdf_path)
        paginas = len(doc)  # total de páginas
        self.lbl_paginas.setText(f"Hojas: {paginas}")

        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            
            lbl = QLabel()
            lbl.setPixmap(QPixmap.fromImage(img))
            lbl.setAlignment(Qt.AlignCenter)

            # Contenedor con número de página
            contenedor = QWidget()
            vbox_page = QVBoxLayout(contenedor)
            vbox_page.addWidget(lbl)

            # Texto de paginación
            lbl_num = QLabel(f"Página {i} de {paginas}")
            lbl_num.setAlignment(Qt.AlignCenter)
            vbox_page.addWidget(lbl_num)

            self.vbox.addWidget(contenedor)

        doc.close()

    def guardar_como(self):
        fecha_str = datetime.now().strftime("%d_%m_%Y_%I:%M%p")
        sugerencia = f"reporte_{fecha_str}.pdf"
        nueva_ruta, _ = QFileDialog.getSaveFileName(
            self, 
            "Descargar reporte", 
            sugerencia, 
            "PDF Files (*.pdf)"
        )
        if nueva_ruta:
            with open(self.pdf_path, "rb") as f_src:
                with open(nueva_ruta, "wb") as f_dst:
                    f_dst.write(f_src.read())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ReportePDFWindow()
    ventana.show()
    sys.exit(app.exec_())