import uuid
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime
from datetime import timedelta
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.errors import ConnectionFailure
from ModuloHelper.ManagerHelper import Errores
import settings

class ManagerMongoDb:
    def __init__(self):

        settings.readconfig()
        self.MONGO_URL = "mongodb+srv://{0}:{1}@{2}"
        self.MONGODB_HOST = os.getenv("MONGODB_HOST")
        self.MONGODB_USUARIO = os.getenv("MONGODB_USUARIO")
        self.MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
        self.MONGODB_DEFAULT_DB = os.getenv("MONGODB_DEFAULT_DB")
        self.MONGODB_DEFAULT_COLLECTION = os.getenv("MONGODB_DEFAULT_COLLECTION")
        self.MONGODB_ADMIN_COLLECTION = os.getenv("MONGODB_ADMIN_COLLECTION")
        

        self.cliente: MongoClient = None
        self.db: Database = None
        self.cursorpisos: Collection = None
        self.cursoradmin: Collection = None
        self.errores = Errores()

    def conectDB(self):
        try:
            self.cliente = MongoClient(self.MONGO_URL.format(self.MONGODB_USUARIO, self.MONGODB_PASSWORD, 
                                                             self.MONGODB_HOST), ssl_cert_reqs=False)
            self.db = self.cliente[self.MONGODB_DEFAULT_DB]
            self.cursorpisos = self.db[self.MONGODB_DEFAULT_COLLECTION]
            self.cursoradmin = self.db[self.MONGODB_ADMIN_COLLECTION]

        except ConnectionFailure:
            raise Exception("Servidor no disponible")

    def getid_autoincremental(self, idcontador, keyaumentar):
        id_autoincremental = self.cursoradmin.find_one_and_update(
            {"_id": idcontador},
            {"$inc": {keyaumentar: 1}},
            projection={"_id": False},
            upsert=True,
            return_document=ReturnDocument.AFTER

        )
        if id_autoincremental is None:
            return False

        return True, id_autoincremental["cantidadproductos"]

    def altaproducto(self,
                     calle,
                     cp,
                     habitaciones,
                     localidad,
                     numero,
                     banos,
                     wasap,
                     tipocasa,
                     telefonodueno,
                     calledueno,
                     numerodueno,
                     tiponegocio_alquiler,
                     tiponegocio_venta,
                     latitud_txt,
                     longitud_txt,
                     dueno,
                     precioventa,
                     precioalquiler,
                     totalmetros,
                     nombre,
                     precision_txt,
                     datosarchivos
                     ):

        try:
            latitud = float(latitud_txt)
            longitud = float(longitud_txt)

            fecha = datetime.utcnow()
            fechadelta = datetime.utcnow() + timedelta(hours=24)
            iditem = str(uuid.uuid4())

            ok = self.cursorpisos.insert_one(
                {
                    "iditem": iditem,
                    "calle": calle,
                    "tiponegocio_alquiler": tiponegocio_alquiler,
                    "tiponegocio_venta": tiponegocio_venta,
                    "cp": cp,
                    "habitaciones": habitaciones,
                    "precioventa": precioventa,
                    "precioalquiler": precioalquiler,
                    "localidad": localidad,
                    "numero": numero,
                    "banos": banos,
                    "wasap": wasap,
                    "tipocasa": tipocasa,
                    "telefonodueno": telefonodueno,
                    "calledueno": calledueno,
                    "numerodueno": numerodueno,
                    "dueno": dueno,
                    "totalmetros": totalmetros,
                    "medicion": False,
                    "nombre": nombre,
                    "nombrefile": datosarchivos,  # list objects
                    "fecha": fecha,
                    "fechadelta": fechadelta,
                    "datosgps": {
                        "coordenadas": [latitud, longitud],
                        "precision": precision_txt

                    }
                }
            )
            if ok.inserted_id != None:
                return True
            return False

        except ValueError:
            raise Exception("Conversion no posible")

    def comprobarexisteinmueble(self, calle, numero):

        try:
            patron = {"calle": calle, "numero": numero}
            ok = list(self.cursorpisos.find(patron))
            if ok != None:
                if len(ok) <= 0:
                    return True
            return False
        except ValueError:
            raise Exception("no podidod conversion {0} {1}".format(calle, numero))

    def getcantidadproductos(self):
        resultados = self.cursoradmin.find_one({"_id": "contador"}, {"_id": False})
        if resultados == None:
            return False
        return True, resultados["cantidadproductos"]

    def primeracomprobacionadmin(self, usuario, password):
        resultado = self.cursoradmin.find_one({"usuario": usuario, "password": password}, {"_id": False})
        if resultado != None:
            return True, resultado["nombre"]
        return False

    def comprobar_existencia_usuario(self, usuario, password):
        resultado = self.cursoradmin.find_one({"usuario": usuario, "password": password}, {"_id": False})
        if resultado != None:
            if len(resultado) > 0:
                return True
        return False

    def getallproductos(self):
        resultados = list(self.cursorpisos.find({}))
        return resultados

    def get_sin_mediciones(self):
        resultados = list(self.cursorpisos.find({"medicion": False}, {"_id": False}))
        return resultados


    def deleteproducto(self, idproducto):
        ok = self.cursorpisos.delete_one({"_id": ObjectId(idproducto)})
        if ok.deleted_count == 1:

            ok = self.cursoradmin.update_one(
                {"_id": "contador"},
                {"$inc": {"cantidadproductos": -1}}
            )
            if ok.modified_count == 1:
                return True
        return False

    def get_vivienda_porid(self, idvivienda):
        datos = self.cursorpisos.find_one({"iditem": idvivienda}, {"_id": False})
        if len(datos) > 0:
            return datos
        else:
            return None

    def comprobarexiste_iditem(self, iditem):
        resultado = self.cursorpisos.count_documents({"iditem": iditem})
        if resultado == 1:
            return True
        elif resultado > 1:
            raise Exception("id item con mas de 2 documentos {0} ".format(iditem))
        elif resultado <= 0:
            return False

    # todo: medicion todavia falta por hacer
    def actualizacion_producto(self, calle, cp, habitaciones, localidad, numero, banos, wasap, tipocasa,
                               telefonodueno, calledueno, numerodueno, tiponegocio_alquiler, tiponegocio_venta,
                               latitude_gps, longitude_gps, dueno, precioventa, precioalquiler, totalmetros,
                               usuario_que_modificada, precision, datosarchivos, iditem
                               ):

        try:
            latitud = float(latitude_gps)
            longitud = float(longitude_gps)
            fecha = datetime.utcnow()
            ok = self.cursorpisos.find_one_and_update(filter={"iditem": iditem},
                                                      update={"$set":
                                                          {
                                                              {
                                                                  "calle": calle,
                                                                  "tiponegocio_alquiler": tiponegocio_alquiler,
                                                                  "tiponegocio_venta": tiponegocio_venta,
                                                                  "cp": cp,
                                                                  "habitaciones": habitaciones,
                                                                  "precioventa": precioventa,
                                                                  "precioalquiler": precioalquiler,
                                                                  "localidad": localidad,
                                                                  "numero": numero,
                                                                  "banos": banos,
                                                                  "wasap": wasap,
                                                                  "tipocasa": tipocasa,
                                                                  "telefonodueno": telefonodueno,
                                                                  "calledueno": calledueno,
                                                                  "numerodueno": numerodueno,
                                                                  "dueno": dueno,
                                                                  "totalmetros": totalmetros,
                                                                  "usuario_que_modificada": usuario_que_modificada,
                                                                  "nombrefile": datosarchivos,  # list objects
                                                                  "fecha_modificado": fecha,
                                                                  "datosgps": {
                                                                      "coordenadas": [latitud, longitud],
                                                                      "precision": precision

                                                                  }
                                                              }

                                                          }
                                                      }, return_document=False
                                                      )

            if ok.modified_count == 1:
                return self.errores.actualizado_correctamente
            elif ok.modified_count > 1:
                return self.errores.duplicado
            else:
                return self.errores.no_actualizado

        except ValueError:
            raise Exception("no posible conversion")


managermongo = ManagerMongoDb()
managermongo.conectDB()
