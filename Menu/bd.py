import sqlite3
from Clases import *
import hashlib
from datetime import datetime,timezone

db="datos.db"
class Base_Datos():
    
#Crear Tablas
    
    def crear_personas():
        conexion = sqlite3.connect(db)
        try:
            conexion.execute("""CREATE TABLE Persona (
                                    cod_Persona INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Nombre TEXT NOT NULL,
                                    CI TEXT NOT NULL UNIQUE,
                                    Cargo TEXT NOT NULL
                                )""")
            print("Se creo la tabla Persona")
        except sqlite3.OperationalError:
            print("La tabla ya existe")
        conexion.close()


    def crear_Usuarios():
        conexion = sqlite3.connect(db)
        try:
            conexion.execute("""CREATE TABLE Usuarios (
                                    cod_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                                    usuario TEXT NOT NULL UNIQUE,
                                    password TEXT NOT NULL,
                                    estado BOOL DEFAULT 1, 
                                    cod_Persona INTEGER UNIQUE,
                                    FOREIGN KEY (cod_Persona) REFERENCES Persona (cod_Persona)
                                        ON DELETE CASCADE
                                        ON UPDATE CASCADE
                                )""")
            print("Se creo la tabla Usuarios")
        except sqlite3.OperationalError:
            print("La tabla ya existe")
        conexion.close()

    def crear_Robots():
        conexion = sqlite3.connect(db)
        try:
            conexion.execute("""CREATE TABLE Robot (
                                    Cod_Robot INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Nombre TEXT NOT NULL,
                                    Capacidad INTEGER NOT NULL,
                                    Ancho INTEGER NOT NULL,
                                    Largo INTEGER NOT NULL,
                                    Alto INTEGER NOT NULL,
                                    IpRobot TEXT NOT NULL,
                                    IpCamL TEXT NOT NULL,
                                    IpCamR TEXT NOT NULL,
                                    estado BOOL DEFAULT 1
                                )""")
            print("Se creo la tabla")
        except sqlite3.OperationalError:
            print("La tabla ya existe ")
        conexion.close

    def crear_Areas():
        conexion = sqlite3.connect(db)
        try:
            conexion.execute("""CREATE TABLE Area (
                                    Cod_Area INTEGER PRIMARY KEY AUTOINCREMENT,
                                    Nombre TEXT NOT NULL,
                                    Latitud TEXT NOT NULL,
                                    Longitud TEXT NOT NULL,
                                    Ancho TEXT NOT NULL,
                                    Largo TEXT NOT NULL,
                                    Ubicacion TEXT NOT NULL,
                                    Estado BOOL DEFAULT 1
                                )""")
            print("Se creo la tabla")
        except sqlite3.OperationalError:
            print("La tabla ya existe ")
        conexion.close

    def crear_Area_Robot():
        conexion = sqlite3.connect(db)
        try:
            conexion.execute("""CREATE TABLE Area_Robot (
                                    Area_Robot INTEGER PRIMARY KEY AUTOINCREMENT,
                                    estado INTEGER NOT NULL,
                                    Cod_Area INTEGER NOT NULL,
                                    Cod_Robot INTEGER NOT NULL,
                                    Cod_usuario INTEGER NOT NULL,
                                    Fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    tiempo INTEGER,

                                    FOREIGN KEY (Cod_Area) REFERENCES Area(Cod_Area),  
                                    FOREIGN KEY (Cod_Robot) REFERENCES Robot(Cod_Robot)
                                    FOREIGN KEY (Cod_usuario) REFERENCES Usuarios(cod_Usuario)
                                )""")
            print("Se creo la tabla Area_Robot")
        except sqlite3.OperationalError:
            print("La tabla ya existe ")
        conexion.close

    def crear_Matriz():
        conexion = sqlite3.connect(db)
        try:
            conexion.execute("""CREATE TABLE Matriz (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                Cod_Area_Robot INTEGER NOT NULL,
                                Cod_Usuario INTEGER NOT NULL,
                                fecha date NOT NULL,
                                fila INTEGER NOT NULL,
                                columna INTEGER NOT NULL,
                                valor INTEGER,
                                FOREIGN KEY (Cod_Area_Robot) REFERENCES Area(Area_Robot)
                                FOREIGN KEY (Cod_Usuario) REFERENCES Usuario(cod_Usuario)
                                    ON DELETE CASCADE
                                    ON UPDATE CASCADE
                            )""")
            print("se creo la tabla Matriz")
        except sqlite3.OperationalError:
            print("La tabla ya existe")
        conexion.close

#LLenar Tablas

    def hash_password(self,password):
        return hashlib.sha256(password.encode()).hexdigest()

    def llenar_Usuarios(self,datos: Usuarios):
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        password = self.hash_password(datos.password)
        cursor.execute("INSERT INTO Persona (nombre, ci,cargo) VALUES(?,?,?)", (datos.nombre, datos.ci,datos.cargo))
        conexion.commit()
        print("Se agrego Persona")
        cod_Persona = cursor.lastrowid
        cursor.execute("INSERT INTO Usuarios (usuario, password, cod_Persona) VALUES (?, ?, ?)",
                       (datos.user, password, cod_Persona))
        conexion.commit()
        conexion.close()
    
    def Agregar_Robot(self,datos: Robots):
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO Robot (nombre,capacidad,ancho,largo,alto,IpRobot,IpCamL,IpCamR) VALUES(?,?,?,?,?,?,?,?)",(datos.Nombre,datos.Capacidad,datos.Ancho,datos.Largo,datos.Alto,datos.IpRobot,datos.IpCamL,datos.IpCamR))
        conexion.commit()
        print("Se agrego Robot")
        conexion.close

    def Agregar_Area(self,datos: Areas):
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO Area (nombre,latitud,longitud,ancho,largo,ubicacion) VALUES(?,?,?,?,?,?)",(datos.Nombre,datos.Latitud,datos.Longitud,datos.Ancho,datos.Largo,datos.Ubicacion))
        conexion.commit()
        print("Se agrego Area")
        conexion.close

    def Agregar_Area_Robot(self,datos: Area_Robot):
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO Area_Robot (estado,cod_area,cod_robot,cod_usuario) VALUES (?,?,?,?)",(datos.Estado,datos.Area,datos.Robot,datos.Usuario))
        conexion.commit()
        print("se agrego Area_Robot")
        conexion.close

    def agregar_matriz(self,datos: Matriz):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i in range(5):
            for j in range(5):
                self.dato(datos.Area_Robot,datos.Usuario,i,j,datos.Matriz[i][j],fecha)
        print("Se agrego Matriz")


    def dato(self,area_robot,usuario,fila,columna,valor,fecha):
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO Matriz (Cod_Area_Robot,Cod_Usuario,fila,columna,valor,fecha) VALUES(?,?,?,?,?,?)",(area_robot,usuario,fila,columna,valor,fecha))
        conexion.commit()
        conexion.close

#Listar Datos de tablas

    
    def Listar_Usuarios(self):
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        sql = " SELECT Persona.cod_Persona, Persona.Nombre, Persona.CI, Persona.Cargo, Usuarios.usuario, Usuarios.password, Usuarios.estado FROM Persona INNER JOIN Usuarios ON Persona.cod_Persona = Usuarios.cod_Persona;"
        cursor.execute(sql)
        registro = cursor.fetchall()
        return registro

    def Listar_Robots(self):
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        sql ="SELECT * FROM Robot ORDER BY  LOWER(Nombre) ASC"
        cursor.execute(sql)
        registro = cursor.fetchall()
        return registro
    
    def Listar_Area(self):
        conexion = sqlite3.connect(db)
        cursor=conexion.cursor()
        sql ="SELECT * FROM area"
        cursor.execute(sql)
        registro = cursor.fetchall()
        return registro
    
    def Listar_Area_Robot(self):
        conexion = sqlite3.connect(db)
        cursor=conexion.cursor()
        sql ="SELECT area_robot.Area_Robot,area_robot.fecha, area.nombre,robot.nombre,usuarios.usuario  " \
        "FROM area_robot " \
        "INNER JOIN area ON area_robot.cod_area = area.cod_area " \
        "INNER JOIN robot ON area_robot.cod_robot = robot.cod_robot " \
        "INNER JOIN Usuarios ON area_robot.cod_usuario = Usuarios.cod_usuario "
        cursor.execute(sql)
        registro = cursor.fetchall()
        return registro
    
    def Datos_matriz(self,area):
        matriz = [[0 for _ in range(5)]for _ in range(5)]
        conexion = sqlite3.connect(db)
        cursor=conexion.cursor()
        cursor.execute("SELECT * FROM MATRIZ WHERE MATRIZ.COD_AREA_ROBOT = ?",(area,))
        registro = cursor.fetchall()
        print(registro)
        for i in registro:
            fila = int(i[4])
            colum = int(i[5])
            matriz[fila][colum]=i[6]
        return matriz
            
    
    def obtenerIDUsuario(self,nombre):
        conexion = sqlite3.connect("datos.db")
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT * FROM Persona WHERE nombre = ?",(nombre,))
            resultados = cursor.fetchall()
            if resultados:
                for row in resultados:
                    return row[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error al acceder a la base de datos: {e}")
        finally:
            conexion.close()

    def obtenerIDRobot(self,nombre):
        conexion = sqlite3.connect("datos.db")
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT * FROM Robot WHERE nombre = ?",(nombre,))
            resultados = cursor.fetchall()
            if resultados:
                for row in resultados:
                    return row[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error al acceder a la base de datos: {e}")
        finally:
            conexion.close()
            
    def obtenerIDArea(self,nombre):
        conexion = sqlite3.connect("datos.db")
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT * FROM Area WHERE nombre = ?",(nombre,))
            resultados = cursor.fetchall()
            if resultados:
                for row in resultados:
                    return row[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"Error al acceder a la base de datos: {e}")
        finally:
            conexion.close()

    def Modificar(self,tabla,columnas,valores,condicion,valores_condicion):
        try:
            conexion = sqlite3.connect(db)
            cursor = conexion.cursor()
            columnas_aux = ", ".join([f"{col}= ?" for col in columnas])
            query = f"UPDATE {tabla} SET {columnas_aux} WHERE {condicion}"
            cursor.execute(query, valores + list(valores_condicion))

            conexion.commit()
            print(f"{cursor.rowcount} filas actualizadas")
        except sqlite3.Error as e:
            print(f"Error al actualizar los datos: {e}")

        finally:
            if conexion:
                conexion.close()

    def Deshabilitar(self,tabla, id,condicion):
        try:
            conexion = sqlite3.connect(db)
            cursor = conexion.cursor()
            query = f"UPDATE {tabla} SET estado = 0 WHERE {condicion} = {id}"
            cursor.execute(query)
            conexion.commit()
            print(f"{cursor.rowcount} deshabilitado")
        except sqlite3.Error as e:
            print(f"Error al deshabilitar el usuario: {e}")

    def Habilitar(self,tabla,id,condicion):
        print(tabla,id)
        try:
            conexion = sqlite3.connect(db)
            cursor = conexion.cursor()
            query = f"UPDATE {tabla} SET estado = 1 WHERE {condicion} = {id}"
            cursor.execute(query)
            conexion.commit()
            print(f"{cursor.rowcount} deshabilitado")
        except sqlite3.Error as e:
            print(f"Error al deshabilitar el usuario: {e}")
    
    
    #crear_personas()
    #crear_Usuarios()
    #crear_Robots()
    #crear_Areas()
    #crear_Matriz()
    #crear_Area_Robot()

    def ver():
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()
        nombre = 'Wrench'
        cursor.execute("SELECT * FROM Robot WHERE nombre = ?",(nombre,))
        registros = cursor.fetchall()  
        if registros:
            print("Datos de la tabla Robot:")
            print("ID | Nombre | Ancho | Largo | IpRobot | IpCamL | IpCamR ")
            print("-"*30)
            for registro in registros:
                print(f"{registro[0]} | {registro[1]} | {registro[2]} | {registro[3]} | {registro[4]} | {registro[5]} | {registro[6]}")
            
        else:
            print("No hay datos")

        conexion.close()

    def ver_Datos_Persona_Usuarios():
        conexion = sqlite3.connect(db)
        cursor = conexion.cursor()

        try:
            # Consulta que une las tablas Persona y Login mediante cod_Persona
            sql = """
            SELECT Persona.cod_Persona, Persona.Nombre, Persona.CI, Persona.Cargo, Usuarios.usuario, Usuarios.password
            FROM Persona
            INNER JOIN Usuarios ON Persona.cod_Persona = Usuarios.cod_Persona;
            """
            cursor.execute(sql)
            registros = cursor.fetchall()

            # Mostrar los registros encontrados
            if registros:
                print("Datos de las tablas Persona y Login relacionados:")
                for registro in registros:
                    print(f"ID: {registro[0]}, Nombre: {registro[1]}, CI: {registro[2]}, Cargo: {registro[3]}, Usuario: {registro[4]}, Password: {registro[5]}")
            else:
                print("No se encontraron registros relacionados.")
        
        except sqlite3.Error as e:
            print(f"Error al consultar los datos: {e}")
        
        finally:
            conexion.close()

    def vista_Matriz(cod_area):
        matriz = [[0 for _ in range(5)]for _ in range(5)]
        conexion = sqlite3.connect(db)
        cursor=conexion.cursor()
        sql = "SELECT * FROM Matriz WHERE Matriz.Cod_Area_Robot = 1"
        cursor.execute("SELECT * FROM Matriz WHERE Matriz.Cod_Area_Robot = ?",(cod_area,))
        registro = cursor.fetchall()
        for i in registro:
            fila = int(i[3])
            colum = int(i[4])
            matriz[fila][colum]=i[5]
        print(matriz)
            

    #vista_Matriz()
    #ver()      
    #ver_Datos_Persona_Usuarios()

    