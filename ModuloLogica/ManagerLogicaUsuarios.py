import base64
import os
import sys
from datetime import datetime
from werkzeug.utils import secure_filename
import math
from flask import session

from ModuloMongodb.ManagerMongodb import managermongo
from ModuloHelper.ManagerHelper import Errores
from ModuloRedis.ManagerRedis import ManagerRedis
from ModuloConstantes.Constantes import *
from ModuloSQL.ManagersqlAdministradores import Managersql


class ManagerLogicaUsuarios:
    def __init__(self):
        self.errores = Errores()

    def comprobar_existencia_usuario(self, usuario, password):
        if usuario == "" or password == "" or usuario is None or password is None:
            return False

        # realizamos la comprobacion del usuario a traves de sql, podriamos realizar la
        # comprobacion con una db nosql, mucho mas rapida que sql
        resultado = Managersql.insertar_usuario(nick_usuario=usuario, password=password)
        if resultado is not None:
            return resultado
        return False
