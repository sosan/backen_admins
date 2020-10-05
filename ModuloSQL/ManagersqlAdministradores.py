import os
import pymysql

from ModuloHelper.ManagerHelper import Errores
from ModuloSQL.Sql import DbMysql


class Managersql:
    def __init__(self):
        self.errores = Errores()
        self.dbmysql = DbMysql()

    def insertar_nuevo_admin(self, formulario, permiso):
        # metodo donde insertamos los datos que nos entregan desde un formulario
        sql = """INSERT INTO inmobiliaria.administradores(usuario, clave, nombre, apellidos, email, id_roles, telefono, imagen_perfil) 
        VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}", "{7}")""".format(
            formulario["usuario"].lower().strip(),
            formulario["password"].lower().strip(),
            formulario["nombre"].lower().strip(),
            formulario["apellidos"].lower().strip(),
            formulario["email"].lower().strip(),
            permiso,  # -------------- PERMISO ---------------
            formulario["telf"].lower().strip(),
            formulario["imagen_perfil"].lower().strip())
        numero_row_insertados = self.dbmysql.query(sql)
        if numero_row_insertados is not None:
            if numero_row_insertados == 1:
                return True
        return False

    def obtener_todos_administradores(self):
        sql = 'SELECT * FROM inmobiliaria.administradores'
        resultados = self.dbmysql.query(sql)
        if resultados:
            return resultados
        return None

    def borrar_administrador(self, id_administrador):
        sql = 'DELETE FROM inmobiliaria.administradores WHERE id="{0}"'.format(id_administrador)
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados == 1:
                return True
        return False

    def modificar_administrador(self, formulario, id_administrador):
        sql = 'UPDATE inmobiliaria.administradores SET nombre="{0}", apellidos="{1}", telefono="{2}" WHERE id="{3}"'.format(
            formulario["nombre"].lower().strip(),
            formulario["apellidos"].lower().strip(),
            formulario["telefono"].lower().strip(),
            id_administrador)
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados == 1:
                return True
        return False

    def comprobar_permiso(self, usuario, permiso):
        # comprobamos si tiene el permiso 1
        sql = 'SELECT COUNT(id) FROM inmobiliaria.administradores WHERE usuario="{0}" AND id_roles="{1}"'.format(
            usuario.lower().strip(), permiso)
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados[0][0] == permiso:
                return True
        return False

    def comprobar_usuario_admin(self, usuario, password):
        # sql donde buscamos cuantos usuarios coinciden con usuario y password que nos
        # entregan con usuario y password
        # en caso de encontrar a alguien (resultados = 1) devolvemos True
        # en caso de encontrar a mas de uno (resultados > 1) devolvemos False
        # en caso de no encontrar a nadie (resultados = 0) devolvemos False

        sql = 'SELECT COUNT(id) FROM inmobiliaria.administradores WHERE usuario="{0}" AND clave="{1}"'.format(
            usuario.lower().strip(), password.lower().strip())
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados[0][0] == 1:
                return True
        return False

    def comprobar_solo_usuario_admin(self, usuario: str):
        # comprobar solo si existe el usuario
        sql = 'SELECT COUNT(id) FROM inmobiliaria.administradores WHERE usuario="{0}"'.format(usuario.lower().strip())
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados[0][0] == 1:
                return True
        return False

    def obtener_datos_admin(self, usuario, password):
        # enviamos una consulta a sql para obtener el nombre del usuario
        # en caso de que nos devuelva un None enviamos un nombre por defecto
        # significara que ha habido un problema, el nombre esta definido en
        # errores.nombreError, ademas de que tambien controlamos con un True / false
        sql = 'SELECT nombre, imagen_perfil FROM inmobiliaria.administradores WHERE usuario="{0}" AND clave="{1}"'.format(
            usuario.lower().strip(), password.lower().strip())
        # TODO: faltaria controlar mas en caso de que ha habido un error
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if len(resultados) == 1:
                return True, resultados[0]
        return False, self.errores.nombreError

    def comprobar_solo_comercial(self, usuario):
        sql = 'SELECT COUNT(id) FROM inmobiliaria.comerciales_inmobiliaria WHERE usuario="{0}"'.format(
            usuario.lower().strip())
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados[0][0] == 1:
                return True
        return False

    def obtener_todos_comerciales(self):
        sql = 'SELECT * FROM inmobiliaria.comerciales_inmobiliaria'
        resultados = self.dbmysql.query(sql)
        if resultados:
            return resultados
        return None

    def insertar_nuevo_comercial(self, formulario):
        # metodo donde insertamos los datos que nos entregan desde un formulario
        sql = """INSERT INTO inmobiliaria.comerciales_inmobiliaria(usuario, clave, nombre, apellidos, email, telefono, imagen_perfil) 
        VALUES ("{0}", "{1}", "{2}", "{3}", "{4}", "{5}", "{6}")""".format(
            formulario["usuario"].lower().strip(),
            formulario["password"].lower().strip(),
            formulario["nombre"].lower().strip(),
            formulario["apellidos"].lower().strip(),
            formulario["email"].lower().strip(),
            formulario["telf"].lower().strip(),
            formulario["imagen_perfil"].lower().strip())
        numero_row_insertados = self.dbmysql.query(sql)
        if numero_row_insertados is not None:
            if numero_row_insertados == 1:
                return True
        return False

    def borrar_comercial(self, id_comercial):
        sql = 'DELETE FROM inmobiliaria.comerciales_inmobiliaria WHERE id="{0}"'.format(
            id_comercial.lower().strip())
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados == 1:
                return True
        return False

    def modificar_comercial(self, formulario, id_comercial):
        sql = 'UPDATE inmobiliaria.comerciales_inmobiliaria SET nombre="{0}", apellidos="{1}", telefono="{2}" WHERE id="{3}"'.format(
            formulario["nombre"].lower().strip(),
            formulario["apellidos"].lower().strip(),
            formulario["telefono"].lower().strip(),
            id_comercial)
        resultados = self.dbmysql.query(sql)
        if resultados is not None:
            if resultados == 1:
                return True
        return False
