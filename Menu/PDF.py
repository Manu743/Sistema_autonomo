import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QScrollArea,
    QVBoxLayout, QWidget, QPushButton, QFileDialog, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class ReportePDFWindow(QMainWindow):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reporte PDF")
        self.resize(800, 600)

        self.pdf_path = pdf_path

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Área de scroll para visualizar el PDF
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)

        # Contenedor de páginas
        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.vbox = QVBoxLayout(self.container)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar como...")
        self.btn_guardar.clicked.connect(self.guardar_como)
        btn_layout.addWidget(self.btn_guardar)
        layout.addLayout(btn_layout)

        # Mostrar PDF
        self.mostrar_pdf()

    def mostrar_pdf(self):
        doc = fitz.open(self.pdf_path)
        for page in doc:
            pix = page.get_pixmap()
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            lbl = QLabel()
            lbl.setPixmap(QPixmap.fromImage(img))
            self.vbox.addWidget(lbl)
        doc.close()

    def guardar_como(self):
        nueva_ruta, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", "reporte.pdf", "PDF Files (*.pdf)")
        if nueva_ruta:
            with open(self.pdf_path, "rb") as f_src:
                with open(nueva_ruta, "wb") as f_dst:
                    f_dst.write(f_src.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ReportePDFWindow("reporte.pdf")
    ventana.show()
    sys.exit(app.exec_())
