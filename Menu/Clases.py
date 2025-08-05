class Robots:
    def __init__(self, Nombre,Capacidad,Ancho,Largo,alto,IpRobot,IpCamL,IpCamR):
        self.Nombre=Nombre
        self.Capacidad=Capacidad
        self.Ancho=Ancho
        self.Largo=Largo
        self.Alto=alto
        self.IpRobot=IpRobot
        self.IpCamL=IpCamL
        self.IpCamR=IpCamR

class Usuarios:
    def __init__(self,nombre,ci,cargo,user,password):
        self.nombre=nombre
        self.ci=ci
        self.cargo=cargo
        self.user=user
        self.password=password


class Areas:
    def __init__(self,nombre,Latitud,longitud,ancho,largo):
        self.Nombre=nombre
        self.Latitud=Latitud
        self.Longitud=longitud
        self.Ancho=ancho
        self.Largo=largo

class Matriz:
    def __init__(self,area,fila,columna,valor):
        self.Area=area
        self.Fila=fila
        self.Columna=columna
        self.Valor=valor
        pass