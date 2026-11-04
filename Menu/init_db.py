"""Inicializa la base de datos local sin datos versionados.

Crea el esquema en datos.db y un usuario administrador cuyas credenciales se
leen de variables de entorno.
"""

import os

from Clases import Usuarios
from bd import Base_Datos


def main():
    Base_Datos.crear_personas()
    Base_Datos.crear_Usuarios()
    Base_Datos.crear_Robots()
    Base_Datos.crear_Areas()
    Base_Datos.crear_Area_Robot()
    Base_Datos.crear_Matriz()

    usuario = os.environ.get("SEED_ADMIN_USER", "admin")
    password = os.environ.get("SEED_ADMIN_PASSWORD")
    if not password:
        raise SystemExit(
            "Definir SEED_ADMIN_PASSWORD antes de crear el usuario administrador."
        )

    Base_Datos().llenar_Usuarios(
        Usuarios("Administrador", "00000000", "Administrador", usuario, password)
    )


if __name__ == "__main__":
    main()
