from Clases import *
from bd import *
# Definir los datos de un usuario
user1 = Usuarios('Manuel Arenas Agrada','5807967','Administrador','Manu743','Manu743_1905')
user2 = Usuarios('Natalia','5674234','Operador','Nat','Nat743')
user3 = Usuarios('Wilfredo','56323456','Operador','Wili','Wili743')

Robot1 = Robots('Robot1',5,50,80,12,'192.168.1.101','192.168.1.111','192.168.1.121')
Robot2 = Robots('Robot2',5,50,80,20,'192.168.1.102','192.168.1.112','192.168.1.122')
Robot3 = Robots('Robot3',5,50,80,21,'192.168.1.103','192.168.1.113','192.168.1.123')

Area1 = Areas('Area1','','',150,150,'Area1')
Area2 = Areas('Area2','','',200,150,'Area2')
Area3 = Areas('Area3','','',150,200,'Area3')

Busqueda1 = Area_Robot(1,1,1,1,'')
Busqueda2 = Area_Robot(1,2,2,1,'')
Busqueda3 = Area_Robot(2,2,3,1,'')
Busqueda4 = Area_Robot(3,3,3,1,'')

matriz = [[ 1,  1,  1,  2,  1],
          [ 1,  1,  3,  1,  1],
          [ 1,  1,  1,  3,  2],
          [ 1,  1,  1,  1,  2],
          [ 2,  2,  3,  1,  1]]



busqueda = Matriz('1','1',matriz)
# Crear una instancia de la clase Base_Datos
db_manager = Base_Datos()

# Llamar al método llenar_Usuarios con el argumento correcto
db_manager.agregar_matriz(busqueda)

#db_manager.llenar_Usuarios(user1)
#db_manager.llenar_Usuarios(user2)
#db_manager.llenar_Usuarios(user3)

#db_manager.Agregar_Robot(Robot1)
#db_manager.Agregar_Robot(Robot2)
#db_manager.Agregar_Robot(Robot3)

#db_manager.Agregar_Area(Area1)
#db_manager.Agregar_Area(Area2)
#db_manager.Agregar_Area(Area3)

#db_manager.Agregar_Area_Robot(Busqueda1)
#db_manager.Agregar_Area_Robot(Busqueda2)
#db_manager.Agregar_Area_Robot(Busqueda3)
#db_manager.Agregar_Area_Robot(Busqueda4)
