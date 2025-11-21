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
    def __init__(self,nombre,Latitud,longitud,ancho,largo,ubicacion):
        self.Nombre=nombre
        self.Latitud=Latitud
        self.Longitud=longitud
        self.Ancho=ancho
        self.Largo=largo
        self.Ubicacion=ubicacion

class Matriz:
    def __init__(self,area_robot,usuario,matriz):
        self.Area_Robot=area_robot
        self.Usuario=usuario
        self.Matriz=matriz

class Area_Robot:
    def __init__(self,estado,area,robot,usuario,tiempo):
        self.Estado=estado
        self.Area=area
        self.Robot=robot
        self.Usuario=usuario
        self.Tiempo=tiempo
        