
from PyQt5.QtWidgets import QMainWindow, QApplication,QLineEdit,QMessageBox
from PyQt5.QtGui import QGuiApplication,QIcon
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi 
from PyQt5.QtCore import Qt
import sys
import subprocess
import sqlite3
import hashlib

class Login(QMainWindow):
	def __init__(self):
		super(Login, self).__init__()
		loadUi('./GUI Login/design.ui', self)

		self.click_posicion = None
		self.bt_minimize.clicked.connect(lambda :self.showMinimized())
		self.bt_close.clicked.connect(lambda: self.close())
		self.Loguin.clicked.connect(self.loguin)
           
        # Eliminar barra de titulo y opacidad
		self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
		self.setWindowOpacity(1)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

		# SizeGrip
		self.gripSize = 10
		self.grip = QtWidgets.QSizeGrip(self)
		self.grip.resize(self.gripSize, self.gripSize)
		# mover ventana
		self.frame_superior.mouseMoveEvent = self.mover_ventana


		icon_user = QIcon("./GUI Login/image/user.png")
		icon_lock = QIcon("./GUI Login/image/candado.png")
		self.Usuario.addAction(icon_user, QLineEdit.LeadingPosition) #QLineEdit.TrailingPosition		
		self.Password.addAction(icon_lock, QLineEdit.LeadingPosition) 



	def prueba(self):
		#print("loguin")
		self.close()
		subprocess.run(["python", "./Menu/Menu.py"])

	## SizeGrip
	def resizeEvent(self, event):
		rect = self.rect()
		self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

	## mover ventana
	def mousePressEvent(self, event):
		self.click_posicion = event.globalPos()
	
	def mover_ventana(self, event):
		if self.isMaximized() == False:
			if event.buttons() == QtCore.Qt.LeftButton:
				self.move(self.pos() + event.globalPos() - self.click_posicion)
				self.click_posicion = event.globalPos()
				event.accept()
		if event.globalPos().y() <=5 or event.globalPos().x() <=5 :
			self.showMaximized()
		else:
			a = any
			#self.showNormal()
			#self.bt_normal.hide()
			#self.bt_maximize.show()
	    
	def loguin(self):
		
		user = self.Usuario.text()
		password = self.Password.text()

		if self.validar_usuario(user,password):
			self.close()
			subprocess.run(["python", "./Menu/Menu.py"])
		else:
			QMessageBox.warning(self, "Login Fallido", "Usuario o contraseña incorrectos.")
			self.Password.clear()

	def hash(self,password):
		return hashlib.sha256(password.encode()).hexdigest()

	def validar_usuario(self, username, password):
		conn = sqlite3.connect('datos.db')
		cursor = conn.cursor()
		password_hash = self.hash(password)
        # Verificar si el usuario y contraseña coinciden
		cursor.execute('SELECT * FROM Usuarios WHERE usuario = ? AND password = ? AND estado = 1', (username, password_hash))
		result = cursor.fetchone()
		conn.close()
        # Si se encuentra un resultado, el login es válido
		if result:
			return True
		else:
			return False


if __name__ == '__main__':
	app = QApplication(sys.argv)
	my_app = Login()
	my_app.show()
	sys.exit(app.exec_())

