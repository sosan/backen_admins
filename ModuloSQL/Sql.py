import os
import pymysql

from ModuloHelper.ManagerHelper import Errores

# configuracion de puertos, path, etc...
import settings


class DbMysql:
    def __init__(self):
        try:
            # leemos la configuracion desde el archivo .env que esta en la raiz junto a main.py
            # usamos este metodo ya que no es una buena practica exponer las variables sensibles(password, usuarios..)
            # al publico. en el gitignore esta añadido .env.
            # si hay que cambiar usuarios, password se cambiaran desde el archivo .env
            settings.readconfig()

            self.errores = Errores()
            # configuracion para poder accederr a mysql. en caso de no encontrar la variable "HOST_MYSQL", etc...
            # se sustituyen por la derecha, "localhost", ...,"". en este caso esta vacio asi dara error de conexion
            # en el caso de que no haya podido leer los datos de la conexion en el archivo .env
            # una vez subido a heroku, docker, hay que exportar/insertar las varialbes de entornos en esos sistemas
            host_mysql = os.getenv("HOST_MYSQL", "localhost")
            user_mysql = os.getenv("USER_MYSQL", "")
            password_mysql = os.getenv("PASSWORD_MYSQL", "")
            database_mysql = os.getenv("DEFAULT_DATABASE_MYSQL", "")

            # conexion de mysql
            self.conexion = pymysql.connect(host=host_mysql, user=user_mysql, password=password_mysql,
                                            database=database_mysql)
            self.cursor = self.conexion.cursor()
        except Exception as error:
            raise Exception("Error al conectar Mysql error=", error)

    def query(self, sql: str):
        """
        metodo donde recibiremos el comando sql que queremos ejecutar. si camibamos de base de datos sql, la integracion
        se realizara en este archivo sql.py
        :param sql: string con el comando sql a ejecutar
        :return: los datos consultados en select, none o  numero de rows actuzalizados
        """
        if "SELECT" in sql:
            self.cursor.execute(sql)
            datos = self.cursor.fetchall()
            return datos
        else:
            self.cursor.execute(sql)
            self.conexion.commit()
            if not self.conexion.get_autocommit():
                if self.cursor.rowcount <= 0:
                    return None

                return self.cursor.rowcount

    # Cerrar base de datos
    def cerrar(self):
        self.conexion.close()
