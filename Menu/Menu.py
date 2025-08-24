from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QWidget, QTableWidgetItem, QComboBox, QVBoxLayout, QLabel,QMessageBox,QPushButton
from PyQt5.QtGui import QGuiApplication,QIcon,QImage,QPixmap
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi 
from PyQt5.QtCore import Qt,QUrl
import sys, subprocess
from Clases import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from bd import *
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Control')))
#import Control
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'PDF')))
import PDF
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtCore import QTimer
#from PyQt5.QtGui import QImage
import fitz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet


class MostrarMapa(QObject):
    locationSelected = pyqtSignal(float, float)
    @pyqtSlot(float,float)
    def emitirlocalizacion(self,lat,long):
        self.locationSelected.emit(lat,long)
	

class Pantallas(QMainWindow):
	def __init__(self):
		self.modo=0
		self.modoRobot=0
		self.modoArea=0
		self.robots = []
		self.Areas = []
		self.valores = []
		self.valoresRobots = []
		self.valoresAreas = []
		self.detalle = []
		self.estado = 1
		self.aux = 0
		#uso de base de datos
		self.Total = Base_Datos()


		#uso de pantallas
		super(Pantallas, self).__init__()
		loadUi('./Menu/Prototipo.ui', self)
		self.showMaximized()
		
		self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
		self.setWindowOpacity(1)
		self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

		self.cargarRobots()
		self.cargarAreas()
		self.robotsId = [""]*6
		self.robotsNombre = [""]*6
		self.AreasId = [""]*6
		self.AreasNombre = [""]*6

		self.Label_Robot1.setText("Desconectado")
		self.Label_Robot1.setAlignment(Qt.AlignCenter) 
		self.Label_Robot2.setText("Desconectado")
		self.Label_Robot2.setAlignment(Qt.AlignCenter) 
		self.Label_Robot3.setText("Desconectado")
		self.Label_Robot3.setAlignment(Qt.AlignCenter) 
		self.Label_Robot4.setText("Desconectado")
		self.Label_Robot4.setAlignment(Qt.AlignCenter) 
		self.Label_Robot5.setText("Desconectado")
		self.Label_Robot5.setAlignment(Qt.AlignCenter) 
		self.Label_Robot6.setText("Desconectado")
		self.Label_Robot6.setAlignment(Qt.AlignCenter) 
		
		self.Agregar_Robot.adjustSize()
		
		self.stackedWidget_3.setCurrentWidget(self.Home_6)
		self.Home_5.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Home_6))
		self.Home_5.clicked.connect(self.reload)
		self.Home_5.clicked.connect(self.reloadAreas)
		
		self.Lista_Robots.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Lista_Robots_2))
		self.Lista_Robots.clicked.connect(self.mostrar_Robots)
		self.Agregar_Robot.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Add_Robot))
		self.Agregar_Robot.clicked.connect(lambda: self.cambiar_Robot(0))
		self.Cancelar_Robot.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Lista_Robots_2))
		self.Modificar_Robot.clicked.connect(lambda: self.cambiar_Robot(1))
		self.Agregar_Robot_2.clicked.connect(lambda: self.add_mod_Robot())
		self.Hab_Des.clicked.connect(lambda: self.hab_Des_Robot())
		self.Tabla_Robots.cellClicked.connect(self.seleccionar_Robot)


		self.Lista_Usuarios.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Lista_Usuarios_2))
		self.Lista_Usuarios.clicked.connect(self.mostrar_usuarios)
		self.Agregar_Usuario.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Add_Usuario))
		self.Agregar_Usuario.clicked.connect(lambda:self.cambiar(0))
		self.Agregar_Usuario_2.clicked.connect(self.add_mod)
		self.Cancelar_Usuario.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Lista_Usuarios_2))
		self.Modificar_Usuario.clicked.connect(lambda:self.cambiar(1))
		self.Deshabilitar_Usuario.clicked.connect(lambda: self.hab_des())
		self.Tabla_Usuarios.cellClicked.connect(self.seleccionar_Usuario)

		self.Historial_5.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Historial_6))
		self.Historial_5.clicked.connect(lambda: self.carga_historial())
		self.Tabla_Historial_3.cellClicked.connect(self.seleccionar_detalles)

		self.Notificacion_3.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Notificaciones_3))
		
		self.Lista_Areas.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Lista_Areas_2))
		self.Lista_Areas.clicked.connect(lambda:self.ver_mapa())
		self.Lista_Areas.clicked.connect(self.mostrar_Areas)
		self.Agregar_Area.clicked.connect(lambda: self.cambiar_Areas(1))
		self.Modificar_Area.clicked.connect(lambda:self.cambiar_Areas(0))
		self.Cancelar_Area.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Lista_Areas_2))
		self.Agregar_Area_3.clicked.connect(lambda:self.add_mod_areas())
		self.Previsualizar.clicked.connect(lambda:self.previsualizar())
		self.table_Areas.cellClicked.connect(self.seleccionar_Area)
		#self.Imagen.clicked.connect(lambda:self.guardar_mapa())
		

		self.Ver1.clicked.connect(lambda: self.controles(0))
		self.Ver2.clicked.connect(lambda: self.controles(1))
		self.Ver3.clicked.connect(lambda: self.controles(2))
		self.Ver4.clicked.connect(lambda: self.controles(3))
		self.Ver5.clicked.connect(lambda: self.controles(4))
		self.Ver6.clicked.connect(lambda: self.controles(5))

		self.Desconectar1.clicked.connect(lambda:self.Quitar_id(0))
		self.Desconectar2.clicked.connect(lambda:self.Quitar_id(1))
		self.Desconectar3.clicked.connect(lambda:self.Quitar_id(2))
		self.Desconectar4.clicked.connect(lambda:self.Quitar_id(3))
		self.Desconectar5.clicked.connect(lambda:self.Quitar_id(4))
		self.Desconectar6.clicked.connect(lambda:self.Quitar_id(5))

		self.CerrarSesion_3.clicked.connect(lambda: self.logout())

		self.BotonAgregar.clicked.connect(self.CargarRobot)


	def logout(self):
		self.close()
		subprocess.run(["python", "./GUI Login/Loguin.py"])

	def controles(self, numero):
		codigo=self.robotsId[numero]
		area = self.AreasId[numero]
		print(f'codigo: {codigo}')
		print(f'area: {area}')
		if codigo !=  "" and area != "":
			#self.close()
			print("control")
			#self.control = Control.control(codigo,area)
			#self.control.show()
		else:
			QMessageBox.warning(self, "Robot no agregado", "Agregue un robot")


	def cargarRobots(self):
		self.comboBox.clear()  
		conexion = sqlite3.connect("datos.db")
		cursor = conexion.cursor()
		try:
			cursor.execute("SELECT Nombre FROM Robot WHERE estado=1 ORDER BY LOWER(Nombre) ASC")
			resultados = cursor.fetchall()
			for row in resultados:
				self.comboBox.addItem(row[0])
				self.robots.append(row[0])
		except sqlite3.Error as e:
			print(f"Error al acceder a la base de datos: {e}")
		finally:
			conexion.close()

	def cargarAreas(self):
		self.AreasCombobox.clear()  
		conexion = sqlite3.connect("datos.db")
		cursor = conexion.cursor()
		try:
			cursor.execute("SELECT Nombre FROM Area WHERE estado=1 ORDER BY LOWER(Nombre) ASC")
			resultados = cursor.fetchall()
			for row in resultados:
				self.AreasCombobox.addItem(row[0])
				self.Areas.append(row[0])
		except sqlite3.Error as e:
			print(f"Error al acceder a la base de datos: {e}")
		finally:
			conexion.close()

	def reload(self):
		self.comboBox.clear()
		for list in self.robots:
			self.comboBox.addItem(list)
	def reloadAreas(self):
		self.AreasCombobox.clear()
		for list in self.Areas:
			self.AreasCombobox.addItem(list)

	def recargar(self,nombre):
		self.comboBox.clear()
		if nombre in self.robots:
			self.robots.remove(nombre)
		for list in self.robots:
			self.comboBox.addItem(list)

	def recargarAreas(self,nombre):
		self.AreasCombobox.clear()
		if nombre in self.Areas:
			self.Areas.remove(nombre)
		for	list in self.Areas:
			self.AreasCombobox.addItem(list)

	def CargarRobot(self):
		if self.aux < 6:
			if self.robots and self.Areas:
				nombreRobot = self.comboBox.currentText()
				idrobot = self.obtenerIDRobot(nombreRobot)
				nombreArea = self.AreasCombobox.currentText()
				idArea = self.Total.obtenerIDArea(nombreArea)
				self.aux = self.aux+1
				self.agregarid(idrobot,nombreRobot,idArea,nombreArea)
				self.recargar(nombreRobot)
				self.recargarAreas(nombreArea)
			else:
				QMessageBox.warning(self, "Limite de robots", "No existen mas robots")	
		else:
			QMessageBox.warning(self, "Limite de robots", "Se a alcanzado el maximo de robots")
		


	def obtenerIDRobot(self,nombre):
		conexion = sqlite3.connect("datos.db")
		cursor = conexion.cursor()
		try:
			cursor.execute("SELECT * FROM Robot WHERE nombre = ?",(nombre,))
			resultados = cursor.fetchall()
			for row in resultados:
				self.comboBox.addItem(row[0])  
		except sqlite3.Error as e:
			print(f"Error al acceder a la base de datos: {e}")
		finally:
			conexion.close()
			return row[0]


	def agregarid(self,id,nombre,idarea,nombrearea):
		for i in range(len(self.robotsId)):
			if not self.robotsId[i]:
				self.robotsId[i] = id
				self.robotsNombre[i] = nombre
				self.AreasId[i] = idarea
				self.AreasNombre[i] = nombrearea
				if i==0:
					self.Label_Robot1.setText(nombre)
					self.Label_Robot1.setAlignment(Qt.AlignCenter) 
				if i==1:
					self.Label_Robot2.setText(nombre)
					self.Label_Robot2.setAlignment(Qt.AlignCenter)
				if i==2:
					self.Label_Robot3.setText(nombre)
					self.Label_Robot3.setAlignment(Qt.AlignCenter)
				if i==3:
					self.Label_Robot4.setText(nombre)
					self.Label_Robot4.setAlignment(Qt.AlignCenter)
				if i==4:
					self.Label_Robot5.setText(nombre)
					self.Label_Robot5.setAlignment(Qt.AlignCenter)
				if i==5:
					self.Label_Robot6.setText(nombre)
					self.Label_Robot6.setAlignment(Qt.AlignCenter) 
				return
		return
	
	def Quitar_id(self, posicion):
		if self.robotsId[posicion]!="":
			self.aux=self.aux-1
			self.robotsId[posicion]=""
			self.robots.append(self.robotsNombre[posicion])
			self.Areas.append(self.AreasNombre[posicion])
			self.robots.sort(key=str.lower)
			self.Areas.sort(key=str.lower)
			self.comboBox.clear()
			self.AreasCombobox.clear()
			for lista in self.robots:
				self.comboBox.addItem(lista)
			for lista in self.Areas:
				self.AreasCombobox.addItem(lista)
			self.robotsNombre[posicion]=""
			self.AreasNombre[posicion]=""
			i=posicion
			nombre="Desconectado"
			if i==0:
				self.Label_Robot1.setText(nombre)
				self.Label_Robot1.setAlignment(Qt.AlignCenter) 
			if i==1:
				self.Label_Robot2.setText(nombre)
				self.Label_Robot2.setAlignment(Qt.AlignCenter)
			if i==2:
				self.Label_Robot3.setText(nombre)
				self.Label_Robot3.setAlignment(Qt.AlignCenter)
			if i==3:
				self.Label_Robot4.setText(nombre)
				self.Label_Robot4.setAlignment(Qt.AlignCenter)
			if i==4:
				self.Label_Robot5.setText(nombre)
				self.Label_Robot5.setAlignment(Qt.AlignCenter)
			if i==5:
				self.Label_Robot6.setText(nombre)
				self.Label_Robot6.setAlignment(Qt.AlignCenter) 
		else:
			QMessageBox.warning(self, "No tiene conexion", "No tiene robot conectado")

	def mostrar_usuarios(self):
		datos = self.Total.Listar_Usuarios()
		i = len(datos)
		self.Tabla_Usuarios.setRowCount(i)
		tablerow = 0
		for row in datos:
			if row[6]:
				estado='Activo'
			else:
				estado='Inactivo'
			self.Tabla_Usuarios.setItem(tablerow,0,QtWidgets.QTableWidgetItem(row[1]))
			self.Tabla_Usuarios.setItem(tablerow,1,QtWidgets.QTableWidgetItem(row[2]))
			self.Tabla_Usuarios.setItem(tablerow,2,QtWidgets.QTableWidgetItem(row[3]))
			self.Tabla_Usuarios.setItem(tablerow,3,QtWidgets.QTableWidgetItem(row[4]))
			self.Tabla_Usuarios.setItem(tablerow,4,QtWidgets.QTableWidgetItem(estado))
			tablerow +=1

		for row in range(self.Tabla_Usuarios.rowCount()):
			for col in range(self.Tabla_Usuarios.columnCount()):
				item = self.Tabla_Usuarios.item(row, col)
				if item:  
					item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		header = self.Tabla_Usuarios.horizontalHeader()
		header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

	def mostrar_Robots(self):
		datos = self.Total.Listar_Robots()
		i = len(datos)
		self.Tabla_Robots.setRowCount(i)
		tablerow = 0
		for row in datos:
			capacidad = str(row[2])
			ancho = str(row[3])
			largo = str(row[4])
			alto = str(row[5])
			self.Tabla_Robots.setItem(tablerow,0,QtWidgets.QTableWidgetItem(row[1]))
			self.Tabla_Robots.setItem(tablerow,1,QtWidgets.QTableWidgetItem(capacidad))
			self.Tabla_Robots.setItem(tablerow,2,QtWidgets.QTableWidgetItem(ancho))
			self.Tabla_Robots.setItem(tablerow,3,QtWidgets.QTableWidgetItem(largo))
			self.Tabla_Robots.setItem(tablerow,4,QtWidgets.QTableWidgetItem(alto))
			self.Tabla_Robots.setItem(tablerow,5,QtWidgets.QTableWidgetItem(row[6]))
			self.Tabla_Robots.setItem(tablerow,6,QtWidgets.QTableWidgetItem(row[8]))
			estado =''
			if row[9]:
				estado ='Activo'
			else:
				estado ='Inactivo'
			self.Tabla_Robots.setItem(tablerow,7,QtWidgets.QTableWidgetItem(estado))
			tablerow +=1
		for row in range(self.Tabla_Robots.rowCount()):
			for col in range(self.Tabla_Robots.columnCount()):
				item = self.Tabla_Robots.item(row, col)
				if item:  
					item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		
		header = self.Tabla_Robots.horizontalHeader()
		header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

	def mostrar_Areas(self):
		datos = self.Total.Listar_Area()
		i = len(datos)
		self.table_Areas.setRowCount(i)
		tablerow = 0
		for row in datos:
			self.table_Areas.setItem(tablerow,0,QtWidgets.QTableWidgetItem(row[1]))
			self.table_Areas.setItem(tablerow,1,QtWidgets.QTableWidgetItem(row[2]))
			self.table_Areas.setItem(tablerow,2,QtWidgets.QTableWidgetItem(row[3]))
			self.table_Areas.setItem(tablerow,3,QtWidgets.QTableWidgetItem(row[4]))
			self.table_Areas.setItem(tablerow,4,QtWidgets.QTableWidgetItem(row[5]))
			tablerow +=1
		for row in range(self.table_Areas.rowCount()):
			for col in range(self.table_Areas.columnCount()):
				item = self.table_Areas.item(row, col)
				if item:  
					item.setFlags(item.flags() & ~Qt.ItemIsEditable)
		header = self.table_Areas.horizontalHeader()
		header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

	def cambiar(self,modo):
		self.modo=modo
		if modo == 0:
			self.Agregar_Usuario_2.setText(" Añadir Usuario ")
			self.Nombre_Completo.clear()
			self.CI_Usuario.clear()
			self.Cargo_Usuario.clear()
			self.Nombre_Usuario.clear()
			self.Contrase_Usuario.clear()
			self.Contrase_Usuario.setReadOnly(False)

		else:
			if not self.valores:
				QMessageBox.warning(self, "Error", "Seleccione un Usuario")
			else:
				self.stackedWidget_3.setCurrentWidget(self.Add_Usuario)
				self.Agregar_Usuario_2.setText(" Modificar Usuario ")
				self.Nombre_Completo.setText(self.valores[0])
				self.CI_Usuario.setText(self.valores[1])
				self.Cargo_Usuario.setText(self.valores[2])
				self.Nombre_Usuario.setText(self.valores[3])
				self.Contrase_Usuario.setReadOnly(True)


	def add_mod(self):
		if self.modo == 0:
			self.agregar_Usuario()
		else:
			self.modificar_User()

	def agregar_Usuario(self):
		nombre = self.Nombre_Completo.text()
		ci = self.CI_Usuario.text()
		cargo = self.Cargo_Usuario.text()
		usuario = self.Nombre_Usuario.text()
		contra = self.Contrase_Usuario.text()
		user = Usuarios (nombre,ci,cargo,usuario,contra)
		print(user.password)
		if nombre != ''and ci != '' and cargo != ''and usuario != '' and contra != '':
			self.Total.llenar_Usuarios(user)
			self.Nombre_Completo.clear()
			self.CI_Usuario.clear()
			self.Cargo_Usuario.clear()
			self.Nombre_Usuario.clear()
			self.Contrase_Usuario.clear()
			self.mostrar_usuarios()
			self.stackedWidget_3.setCurrentWidget(self.Lista_Usuarios_2)


	def agregar_Robot(self):
		Ip_Robot = self.Ip_Robot.text()
		Ip_CamL = self.Ip_Cam_L.text()
		nombre = self.Nombre_Robot.text()
		capacidad = self.Capacidad_Robot.text()
		ancho = self.Ancho_Robot.text()
		largo = self.Largo_Robot.text()
		alto = self.Alto_Robot.text()
		if Ip_Robot != '' and Ip_CamL != '' and nombre != '' and capacidad != '' and ancho != '' and largo != '' and alto != '':
			robot = Robots(
				self.Nombre_Robot.text(),
				self.Capacidad_Robot.text(),
				self.Ancho_Robot.text(),
				self.Largo_Robot.text(),
				self.Alto_Robot.text(),
				self.Ip_Robot.text(),
				self.Ip_Cam.text(),
			)
			self.Total.Agregar_Robot(robot)
			self.robots.append(robot.Nombre)
			self.robots.sort(key=str.lower)
			self.comboBox.clear()
			for lista in self.robots:
				self.comboBox.addItem(lista)
				
			self.Ip_Robot.clear()
			self.Ip_Cam.clear()
			self.Nombre_Robot.clear()
			self.Capacidad_Robot.clear()
			self.Ancho_Robot.clear()
			self.Largo_Robot.clear()
			self.Alto_Robot.clear()
			self.mostrar_Robots()
			self.stackedWidget_3.setCurrentWidget(self.Lista_Robots_2)

	def agregar_Areas(self):
		nombre = self.Nombre_Area.text()
		latitud = self.Latitud_Area.text()
		longitud = self.Longitud_Area.text()
		Ancho = self.Ancho_Area.text()
		Largo = self.Largo_Area.text()
		ubicacion = '../menu/Imagenes/'+nombre+'.png'
		if nombre !='' and latitud != '' and longitud != '' and Ancho != '' and Largo != '':
			area = Areas(nombre,latitud,longitud,Ancho,Largo,ubicacion)
			self.Total.Agregar_Area(area)
			self.guardar_mapa(area.Nombre)
			self.Nombre_Area.clear()
			self.Latitud_Area.clear()
			self.Longitud_Area.clear()
			self.Ancho_Area.clear()
			self.Largo_Area.clear()
			self.mostrar_Areas()
			self.stackedWidget_3.setCurrentWidget(self.Lista_Areas_2)

	def seleccionar_Usuario(self,row,colum):
		self.valores.clear()
		columna = self.Tabla_Usuarios.columnCount()
		for col in range(columna):
			item = self.Tabla_Usuarios.item(row, col)
			if item is not None:
				self.valores.append(item.text())
			else:
				self.valores.append("")
		if self.valores[4] == 'Inactivo':
			self.Deshabilitar_Usuario.setText("Habilitar Usuario")
		else:
			self.Deshabilitar_Usuario.setText("Deshabilitar Usuario")


	def modificar_User(self):
		nombre = self.Nombre_Completo.text()
		ci = self.CI_Usuario.text()
		cargo = self.Cargo_Usuario.text()
		usuario = self.Nombre_Usuario.text()
		tabla = "Persona"
		columnas = ["Nombre", "CI", "Cargo"]
		valores = [nombre,ci,cargo]
		condicion = "cod_Persona = ?"
		id = self.Total.obtenerIDUsuario(self.valores[0])
		valores_condicion = (id,)
		print(valores,condicion,id)
		self.Total.Modificar(tabla,columnas,valores,condicion,valores_condicion)
		self.stackedWidget_3.setCurrentWidget(self.Lista_Usuarios_2)
		self.mostrar_usuarios()
		self.valores.clear()
	
	def hab_des(self):
		if not self.valores:
			QMessageBox.warning(self, "Error", "Seleccione un usuario")
		else:
			estado = self.valores[4]
			if estado == 'Activo':
				self.deshabilitar()
			else:
				self.habilitar()

	def deshabilitar(self):
		if not self.valores:
			QMessageBox.warning(self, "Error", "Seleccione un Usuario")
		else:
			id = self.Total.obtenerIDUsuario(self.valores[0])
			tabla = 'Usuarios'
			condicion = 'cod_persona'
			self.Total.Deshabilitar(tabla,id,condicion)
			self.mostrar_usuarios()
			self.valores.clear()
	
	def habilitar(self):
		if not self.valores:
			QMessageBox.warning(self, "Error", "Seleccione un Usuario")
		else:
			id = self.Total.obtenerIDUsuario(self.valores[0])
			tabla = 'Usuarios'
			condicion = 'cod_persona'
			self.Total.Habilitar(tabla,id,condicion)
			self.mostrar_usuarios()
			self.valores.clear()


	def seleccionar_Robot(self,row,colum):
		self.valoresRobots.clear()
		columna = self.Tabla_Robots.columnCount()
		for col in range(columna):
			item = self.Tabla_Robots.item(row, col)
			if item is not None:
				self.valoresRobots.append(item.text())
			else:
				self.valoresRobots.append("")
		self.botonhab()

	def cambiar_Robot(self,modo):
		self.modoRobot = modo
		if modo == 0:
			self.Agregar_Robot_2.setText("Añadir Robot")
			self.Nombre_Robot.clear()
			self.Capacidad_Robot.clear()
			self.Ancho_Robot.clear()
			self.Largo_Robot.clear()
			self.Ip_Robot.clear()
			self.Ip_Cam.clear()
		else:
			if not self.valoresRobots:
				QMessageBox.warning(self, "Error", "Seleccione un robot")
			else:
				if self.valoresRobots[0] in self.robotsNombre:
					QMessageBox.warning(self, "Error", "Desconecte un Robot")
				else:
					self.Modificar_Robot.clicked.connect(lambda: self.stackedWidget_3.setCurrentWidget(self.Add_Robot))
					self.Agregar_Robot_2.setText("Modificar Robot")
					self.Nombre_Robot.setText(self.valoresRobots[0])
					self.Capacidad_Robot.setText(self.valoresRobots[1])
					self.Ancho_Robot.setText(self.valoresRobots[2])
					self.Largo_Robot.setText(self.valoresRobots[3])
					self.Alto_Robot.setText(self.valoresRobots[4])
					self.Ip_Robot.setText(self.valoresRobots[5])
					self.Ip_Cam.setText(self.valoresRobots[6])
		
	def modificarRobot(self):
		Ip_Robot = self.Ip_Robot.text()
		Ip_CamL = self.Ip_Cam.text()
		nombre = self.Nombre_Robot.text()
		capacidad = self.Capacidad_Robot.text()
		ancho = self.Ancho_Robot.text()
		largo = self.Largo_Robot.text()
		alto = self.Alto_Robot.text()
		tabla = "Robot"
		columnas = ["Nombre", "Capacidad", "Ancho", "Largo","Alto", "IpRobot", "IpCamL", "IpCamR"]
		valores = [nombre,capacidad,ancho,largo,alto,Ip_Robot,Ip_CamL]
		condicion = "cod_Robot = ?"
		id = self.Total.obtenerIDRobot(self.valoresRobots[0])
		valores_condicion = (id,)
		self.Total.Modificar(tabla,columnas,valores,condicion,valores_condicion)
		self.stackedWidget_3.setCurrentWidget(self.Lista_Robots_2)
		self.mostrar_Robots()
		self.robots.remove(self.valoresRobots[0])
		self.valoresRobots.clear()
		self.robots.append(nombre)
		self.robots.sort(key=str.lower)

		

	def add_mod_Robot(self):
		if self.modoRobot == 0:
			self.agregar_Robot()
		else:
			self.modificarRobot()

	def botonhab(self):
		if self.valoresRobots[7] == 'Activo':
			self.Hab_Des.setText("Deshabilitar")
		else:
			self.Hab_Des.setText("Habilitar")

	def hab_Des_Robot(self):
		if not self.valoresRobots:
			QMessageBox.warning(self, "Error", "Seleccione un Robot")
		else:
			id = self.Total.obtenerIDRobot(self.valoresRobots[0])
			print(self.robots)
			id = self.obtenerIDRobot(self.valoresRobots[0])
			print(id)
			print(self.robots)
			if self.robots and  id not in self.robotsId:
				if self.valoresRobots[7] == 'Activo':
					self.Deshabilitar_Robot(id)
					self.mostrar_Robots()
				else:
					self.Habilitar_Robot(id)
					self.mostrar_Robots()
			else:
				QMessageBox.warning(self, "Error", "El robot esta conectado")

		
	def Deshabilitar_Robot(self,id):
		tabla ='robot'
		condicion ='Cod_Robot'
		self.Total.Deshabilitar(tabla,id,condicion)
		self.robots.remove(self.valoresRobots[0])
		self.valoresRobots.clear()

	
	def Habilitar_Robot(self,id):
		tabla ='robot'
		condicion = 'cod_robot'
		self.Total.Habilitar(tabla,id,condicion)
		self.robots.append(self.valoresRobots[0])
		self.robots.sort(key=str.lower)
		self.valoresRobots.clear()

	def seleccionar_Area(self,row,colum):
		self.valoresAreas.clear()
		columna = self.table_Areas.columnCount()
		for col in range(columna):
			item = self.table_Areas.item(row, col)
			if item is not None:
				self.valoresAreas.append(item.text())
			else:
				self.valoresAreas.append("")

	def cambiar_Areas(self,modo):
		self.modoArea = modo
		if modo:
			self.Nombre_Area.clear()
			self.Latitud_Area.clear()
			self.Longitud_Area.clear()
			self.Ancho_Area.clear()
			self.Largo_Area.clear()
			self.stackedWidget_3.setCurrentWidget(self.Agregar_Area_2)
			self.limpiar()
		else:
			if not self.valoresAreas:
				QMessageBox.warning(self, "Error", "Seleccione un Robot")
			else:
				self.Nombre_Area.setText(self.valoresAreas[0])
				self.Latitud_Area.setText(self.valoresAreas[1])
				self.Longitud_Area.setText(self.valoresAreas[2])
				self.Ancho_Area.setText(self.valoresAreas[3])
				self.Largo_Area.setText(self.valoresAreas[4])
				self.stackedWidget_3.setCurrentWidget(self.Agregar_Area_2)
				self.limpiar()
				self.marcador(self.valoresAreas[1],self.valoresAreas[2])
		
	def add_mod_areas(self):
		print(self.modoArea)
		if self.modoArea:
			self.agregar_Areas()		
		else:
			self.modificarArea()

	def modificarArea(self):
		nombre = self.Nombre_Area.text()
		Latitud = self.Latitud_Area.text()
		Longitud = self.Longitud_Area.text()
		Ancho = self.Ancho_Area.text()
		Largo = self.Largo_Area.text()
		tabla = 'Area'
		columnas = ["nombre","latitud","longitud","ancho","largo"]
		valores = [nombre,Latitud,Longitud,Ancho,Largo]
		condicion = "cod_Area = ?"
		id = self.Total.obtenerIDArea(self.valoresAreas[0])
		valores_condicion=(id,)
		self.Total.Modificar(tabla,columnas,valores,condicion,valores_condicion)
		self.stackedWidget_3.setCurrentWidget(self.Lista_Areas_2)
		self.valoresAreas.clear()
		self.Nombre_Area.clear()
		self.Latitud_Area.clear()
		self.Longitud_Area.clear()
		self.Ancho_Area.clear()
		self.Largo_Area.clear()
		self.mostrar_Areas()
	
	def ver_mapa(self):
		#puente
		self.bridge = MostrarMapa()
		self.bridge.locationSelected.connect(self.ubicacion)

		if hasattr(self, 'cargar_mapa'):	
			self.centralWidget().layout().removeWidget(self.cargar_mapa)
			self.cargar_mapa.deleteLater()
			del self.cargar_mapa

		#area de mapa
		self.cargar_mapa = QWebEngineView(self.mapa)
		ruta = "file:///../Menu/mapa.html"
		self.cargar_mapa.loadFinished.connect(self.inyectar)
		self.cargar_mapa.load(QUrl(ruta))

		#conexion
		self.channel = QWebChannel()
		self.channel.registerObject("pyqt",self.bridge)
		self.cargar_mapa.page().setWebChannel(self.channel)

		ver = self.mapa.layout()
		if not ver:
			ver = QVBoxLayout(self.mapa)
			self.mapa.setLayout(ver)
		ver.addWidget(self.cargar_mapa,alignment=Qt.AlignCenter)
		self.cargar_mapa.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		ver.addWidget(self.cargar_mapa)

	def inyectar(self):
		if not hasattr(self, "channel_initialized"):
			self.channel_initialized = True  
			#self.channel = QWebChannel()
			#self.channel.registerObject("pyqt", self.bridge)
			self.cargar_mapa.page().setWebChannel(self.channel)


	def ubicacion(self,lat,long):
		latitud = str(lat)
		longitud = str(long)
		self.Latitud_Area.setText(latitud)
		self.Longitud_Area.setText(longitud)

	def marcador(self,lat,long):
		js_code = f"cargaMarcador({lat}, {long});"
		self.cargar_mapa.page().runJavaScript(js_code)

	def limpiar(self):
		self.cargar_mapa.page().runJavaScript("limpiar()")

	def previsualizar(self):
		largo = self.Largo_Area.text()
		ancho = self.Ancho_Area.text()
		latitud = self.Latitud_Area.text()
		longitud = self.Longitud_Area.text()
		if largo != '' and ancho != '' and latitud != '' and longitud != '':
			self.cargar_mapa.page().runJavaScript(f"area({latitud},{longitud},{ancho},{largo})")

	def guardar_mapa(self,nombre):
		print("entra")
		if not hasattr(self,"cargar_mapa"):
			print("mapa no cargado")
			return
		
		def limpiar_mapa(_):
			print("limpia")

			def recibir_bounds(bounds):
				if not bounds:
					print("no hay area definida")
					return
				print("puntos: ",bounds)

				def capturar():
					imagenpix = self.cargar_mapa.grab()
					if imagenpix.isNull():
						print("error")
						return
					
					imagen = imagenpix.toImage()
					x = int(bounds['x'])
					y = int(bounds['y'])
					w = int(bounds['width'])
					h = int(bounds['height'])

					w = max(1, min(w, imagen.width()-x))
					h = max(1, min(h, imagen.height()-y))

					recorte = imagen.copy(x,y,w,h)
					if recorte.isNull():
						print("error de recordato")
						return
					
					name = nombre+'.png'
					carpeta = "../Menu/Imagenes"
					if not os.path.exists(carpeta):
						os.makedirs(carpeta)
					completo = os.path.join(carpeta, name)
					recorte.save(completo)

					print(f"imagen guardada {completo}")
				QTimer.singleShot(300,capturar)
			self.cargar_mapa.page().runJavaScript("rectagulo_pixeles();", recibir_bounds)		
		self.cargar_mapa.page().runJavaScript("limpiar();", limpiar_mapa)

	def carga_historial(self):
		datos = [
			(1, "robot", "area", "Manuel"),
			(2,"carlos","area2","Carla")
		]
		i = len(datos)
		self.Tabla_Historial_3.setRowCount(i)
		tablerow = 0
		for row, (codigo,robot,area,supervisor) in enumerate(datos):
			self.Tabla_Historial_3.setItem(row,0,QTableWidgetItem(str(codigo)))
			self.Tabla_Historial_3.setItem(row,1,QTableWidgetItem(robot))
			self.Tabla_Historial_3.setItem(row,2,QTableWidgetItem(area))
			self.Tabla_Historial_3.setItem(row,3,QTableWidgetItem(supervisor))

			boton = QPushButton("Reporte")
			boton.clicked.connect(lambda checked, r=row: self.abrir_reporte())
			self.Tabla_Historial_3.setCellWidget(row, 4, boton)

		header = self.Tabla_Historial_3.horizontalHeader()
		header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

	def seleccionar_detalles(self,row,colum):
		self.detalle.clear()
		columna = self.Tabla_Historial_3.columnCount()
		for col in range(columna):
			item = self.Tabla_Historial_3.item(row, col)
			if item is not None:
				self.detalle.append(item.text())
			else:
				self.detalle.append("")
		print(self.detalle)	

	def abrir_reporte(self):
		area = self.detalle[0]
		Matriz= self.Total.Datos_matriz(area)
		datos ={
			"nombre":self.detalle[3],
			"capacidad":'2',
			"tiempo":'13:00',
			"matriz": Matriz,  # Ejemplo de matriz
			"imagen":'./Menu/Imagenes/1.png'
		}

		ruta = f"./Menu/reportes/reporte_{datos['nombre']}.pdf"
		self.generar_reporte(datos,ruta)

		self.reporte = PDF.ReportePDFWindow(ruta)
		self.reporte.show()

	def generar_reporte(self,datos, output_path):
		doc = SimpleDocTemplate(output_path, pagesize=A4)
		elementos = []

		estilos = getSampleStyleSheet()

		# Título
		elementos.append(Paragraph(f"Reporte de {datos['nombre']}", estilos['Title']))
		elementos.append(Spacer(1, 12))

		# Datos principales
		elementos.append(Paragraph(f"Capacidad: {datos['capacidad']}", estilos['Normal']))
		elementos.append(Paragraph(f"Tiempos: {datos['tiempo']}", estilos['Normal']))
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

		

if __name__ == '__main__':
	app = QApplication(sys.argv)
	my_app = Pantallas()
	my_app.show()
	sys.exit(app.exec_())


