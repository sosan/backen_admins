import base64
import os
import sys
from datetime import datetime
from datetime import timedelta

from ModuloMongodb.ManagerMongodb import managermongo
from ModuloHelper.ManagerHelper import Errores
from ModuloRedis.ManagerRedis import ManagerRedis
from ModuloConstantes.Constantes import *
from ModuloSQL.ManagersqlAdministradores import Managersql


class ManagerLogicaAdministradores:
    def __init__(self):
        self.errores = Errores()
        self.managersql = Managersql()

    def comprobarCamposVacios(self, usuario: str, password: str):
        # simplemente comprobamos que los campso no sean vacios
        if not usuario or not password or usuario is None or password is None:
            return False
        return True

    def comprobar_formulario_vacio(self, formulario: dict):
        # comprobamos la existencia de algun campo vacio
        for elemento in formulario.values():
            if elemento.strip() == "":
                return False
        return True

    def comprobar_existencia_admin(self, usuario, password):
        # realizamos la comprobacion del usuario a traves de sql, podriamos realizar la
        # comprobacion con una db nosql, mucho mas rapida que sql
        # separamos la logica del sql, de la logica que se tenga que realizar
        # con los administradores

        # comprobamos que los campos no esten vacios, etc... aqui se podrian realizar muchas
        # mas comprobaciones
        camposvacios = self.comprobarCamposVacios(usuario, password)
        if camposvacios == False:
            return False

        # enviamos al manager de sql, para que compruebe contra la base de datos
        # realizamos la separacion porque hay muchos dialectos de sql, asi que si cambiamos
        # de basde de datos sql, podemos seguir usando la misma logica, solo cambiariamos
        # la logica interna de "sql.py" ya que es el archivo que realiza la conexion directa y
        # trabaja directamente con la base de datos
        correcto = self.existe_admin(usuario, password)
        if correcto is None or correcto is False:
            # TODO: registrarlo en base de datos redis, para consultar que ha pasado,etc
            # si correcto False
            # devolvemos 2 valores ( correcto = False, nombre = None)
            return False, None

        # ahora necesitamos el nombre del usuario e imagen
        ok, datos_raw = self.managersql.obtener_datos_admin(usuario, password)

        if ok == False:
            return False, None

        datos = {
            "nombre": datos_raw[0],
            "imagen_perfil": datos_raw[1],
        }

        if datos["nombre"] != self.errores.nombreError:
            # devolvemos True, y un diccionario de datos que contiene los datos que queremos
            # True porque ha ido correctamente
            return True, datos
        # aqui devolvemos False porque el nombre coincide con el nombre que saltaria
        # las alarmas ya qye ha habido un error
        # TODO: registrarlo en base de datos redis, para consultar que ha pasado,etc
        return False, None

    def existe_admin(self, usuario: str, password: str):
        # TODO: realizar comprobarciones para que sea mas complicado sql injection
        # que usuario y password no contengan caracteres extraños etc...
        resultado = self.managersql.comprobar_usuario_admin(usuario=usuario, password=password)
        if resultado is None or resultado is False:
            return False
        return True

    def insertar_administrador(self, formulario: dict):
        # TODO: password deber tener cierta complejidad

        formulario_correcto = self.comprobar_formulario_vacio(formulario)
        if formulario_correcto == False:
            return False

        usuario_existe = self.managersql.comprobar_solo_usuario_admin(usuario=formulario["usuario"])
        if usuario_existe == True:
            return False
        insertado_ok = self.managersql.insertar_nuevo_admin(formulario, permiso=2)
        if insertado_ok == False:
            return False
        return True


    def obtener_todos_administradores(self):
        datos = self.managersql.obtener_todos_administradores()
        return datos

    def borrar_administrador(self, id_administrador):
        borrado_correcto = self.managersql.borrar_administrador(id_administrador.lower().strip())
        return borrado_correcto

    def modificar_administrador(self, formulario):
        modificado_correcto = self.managersql.modificar_administrador(formulario, formulario["modificar"].lower().strip())
        return modificado_correcto

    def comprobar_permisos_admin(self, usuario, permiso):
        tiene_permiso = self.managersql.comprobar_permiso(usuario=usuario, permiso=permiso)
        return tiene_permiso

    def obtener_todos_comerciales(self):
        datos = self.managersql.obtener_todos_comerciales()
        return datos

    def borrar_comercial(self, id_comercial):
        borrado_correcto = self.managersql.borrar_comercial(id_comercial.lower().strip())
        return borrado_correcto

    def modificar_comercial(self, formulario):
        modificado_correcto = self.managersql.modificar_comercial(formulario, formulario["modificar"].lower().strip())
        return modificado_correcto

    def insertar_comercial(self, formulario: dict):
        # TODO: mejorar comprobacion con un for
        formulario_correcto = self.comprobar_formulario_vacio(formulario)
        if formulario_correcto == False:
            return False
        usuario_existe = self.managersql.comprobar_solo_comercial(usuario=formulario["usuario"])
        if usuario_existe == True:
            return False
        insertado_ok = self.managersql.insertar_nuevo_comercial(formulario)
        if insertado_ok == False:
            return False
        return True


    def obtener_informe_ultimosdias(self, usuario, cantidad_dias):
        pass

    def obtener_ultimasdias(self, cantidad_dias):
        fecha_fin = datetime.utcnow()
        fecha_inicio = fecha_fin - timedelta(days=cantidad_dias)
        return fecha_inicio, fecha_fin
