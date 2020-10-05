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


class ManagerLogica:
    def __init__(self):
        self.errores = Errores()
        # self.redis = ManagerRedis()
        # heroku
        # self.redis.setupStreamGroup_RedisHeroku_Pool(KEY_STREAM_FOTOS_ANALIZAR, GROUP_STREAM_FOTOS_ANALIZAR)

        # local
        # self.redis.setlocalRedisPool("PRODUCTOR_SUBIRFOTOS")
        # self.redis.setupStreamGroup_RedisLocal(KEY_STREAM_FOTOS_ANALIZAR, GROUP_STREAM_FOTOS_ANALIZAR)

    def comprobarexisteinmueble(self, calle, numero):
        posible_insercion = managermongo.comprobarexisteinmueble(calle, numero)
        return posible_insercion

    def alta_vivienda(self, formulario, maxcontentlength, carpeta_subidas):
        try:
            length_files = int(formulario["files_len"])
            habitaciones = int(formulario["habitaciones"])
            banyos = int(formulario["banos"])
            precioventa = int(formulario["precioventa"])
            precioalquiler = int(formulario["precioalquiler"])
            totalmetros = int(formulario["totalmetros"])

        except ValueError:
            raise Exception("no podido convertir")

        # antes de pasar las imagenes al formato fisico, primero las pasamos por un scan
        # por virusltotal. usaremos redis streams, pero estamos limitados por api publica
        # virustotal (limitado a 4 requests por minuto), el volumen de datos para la api publica
        # no puede ser muy alto. consumer groups de streams quizas sea excesivo para el limite
        # de la api, pero de todas formas lo implementaremos, 1 consumer group con 2 consumers.

        # redis = self.redis.getPoolRedisHeroku(True, "altavivienda")

        datosarchivos = []
        for i in range(0, length_files):
            if "files_{0}_datafile".format(i) in formulario:
                datafile_b64 = formulario["files_{0}_datafile".format(i)]

                tamanoarchivo_bytes = sys.getsizeof(datafile_b64)

                if tamanoarchivo_bytes > maxcontentlength or tamanoarchivo_bytes <= 0:
                    continue

                nombrefile_from_form = secure_filename(formulario["files_{0}_filename".format(i)])

                if datafile_b64 == "" or nombrefile_from_form == "":
                    raise Exception("campo vacio {0}".format(nombrefile_from_form))

                nombrefile = datetime.utcnow().strftime("%d-%b-%Y-%H.%M.%S.%f_") + nombrefile_from_form

                archivo_decodificado = self.getdeencodedfile(datafile_b64)
                # heroku
                # redis.xadd(KEY_STREAM_FOTOS_ANALIZAR, archivo_decodificado)

                # local
                # self.redis.conexion.xadd(KEY_STREAM_FOTOS_ANALIZAR, archivo_decodificado)

                self.control_archivos(carpeta_subidas, datafile_b64, datosarchivos, nombrefile, nombrefile_from_form,
                                      tamanoarchivo_bytes)

        tiponegocio_alquiler = False
        tiponegocio_venta = False
        if "tiponegocio_alquiler" in formulario:
            tiponegocio_alquiler = True

        if "tiponegocio_venta" in formulario:
            tiponegocio_venta = True

        posible_insercion = managermongo.altaproducto(
            formulario["calle"],
            formulario["cp"],
            habitaciones,
            formulario["localidad"],
            formulario["numero"],
            banyos,
            formulario["wasap"],
            formulario["tipocasa"],
            formulario["telefonodueno"],
            formulario["calledueno"],
            formulario["numerodueno"],
            tiponegocio_alquiler,
            tiponegocio_venta,
            formulario["latitude_gps"],
            formulario["longitude_gps"],
            formulario["dueno"],
            precioventa,
            precioalquiler,
            totalmetros,
            formulario["nombre"],
            formulario["precision"],
            datosarchivos

        )

        if posible_insercion == True:
            session["mensajeerror"] = self.errores.insertado_correctamente
            session["anterior_calle"] = formulario["calle"]
            session["anterior_numero"] = formulario["numero"]
        else:
            session["mensajeerror"] = self.errores.no_insertado

    def control_archivos(self, carpeta_subidas, datafile_b64, datosarchivos, nombrefile, nombrefile_from_form,
                         tamanoarchivo_bytes):
        """
        metodo donde controlamos si el archivo subido es correcto

        :param carpeta_subidas: direccion donde subimos los archivos
        :param datafile_b64: archivo en formato base64
        :param datosarchivos: listado de los datos de los archivos
        :param nombrefile: nombre del archivo unico
        :param nombrefile_from_form: nombre original del archivo desde el formulario
        :param tamanoarchivo_bytes: tamano del archivo en bytes
        :return: el listado
        """
        sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        lent = math.floor(math.log(tamanoarchivo_bytes) / math.log(1024))
        tamano_str = "{0} {1}".format(round(tamanoarchivo_bytes / math.pow(1024, lent), 2), sizes[lent])
        datosarchivos.append(
            {
                "nombrefile": nombrefile,
                "nombrefile_fromform": nombrefile_from_form,
                "tamano": tamano_str
            })
        print(os.path.join(carpeta_subidas, nombrefile))
        with open(os.path.join(carpeta_subidas, nombrefile), "wb") as arch:
            cad_cero = datafile_b64.find(',')
            imagen_data64 = datafile_b64[cad_cero + 1:]
            arch.write(base64.decodebytes(imagen_data64.encode()))
            arch.close()

        return datosarchivos

    def mostrarvivienda(self):
        tiponegocio_alquiler = False
        tiponegocio_venta = False

        if "tiponegocio_alquiler" in session:
            session.pop("tiponegocio_alquiler")
            tiponegocio_alquiler = True

        if "tiponegocio_venta" in session:
            session.pop("tiponegocio_venta")
            tiponegocio_venta = True

        variables = {
            "calle": session.pop("calle"),
            "cp": session.pop("cp"),
            "habitaciones": session.pop("habitaciones"),
            "localidad": session.pop("localidad"),
            "numero": session.pop("numero"),
            "banos": session.pop("banos"),
            "wasap": session.pop("wasap"),
            "tipocasa": session.pop("tipocasa"),
            "telefonodueno": session.pop("telefonodueno"),
            "calledueno": session.pop("calledueno"),
            "numerodueno": session.pop("numerodueno"),

            "tiponegocio_alquiler": tiponegocio_alquiler,
            "tiponegocio_venta": tiponegocio_venta,

            "latitude_gps": session.pop("latitude_gps"),
            "longitude_gps": session.pop("longitude_gps"),
            "dueno": session.pop("dueno"),
            "precioventa": session.pop("precioventa"),
            "precioalquiler": session.pop("precioalquiler"),
            "totalmetros": session.pop("totalmetros"),
            "nombre": session.pop("nombre"),
            "precision": session.pop("precision")
        }
        return variables

    def procesar_formulario_noposibleinsercion(self, formulario):
        session["mensajeerror"] = self.errores.duplicado
        session["anterior_calle"] = formulario["calle"]
        session["anterior_numero"] = formulario["numero"]

        session["calle"] = formulario["calle"]
        session["cp"] = formulario["cp"]
        session["habitaciones"] = formulario["habitaciones"]
        session["localidad"] = formulario["localidad"]
        session["numero"] = formulario["numero"]
        session["banos"] = formulario["banos"]
        session["wasap"] = formulario["wasap"]
        session["tipocasa"] = formulario["tipocasa"]
        session["telefonodueno"] = formulario["telefonodueno"]
        session["calledueno"] = formulario["calledueno"]
        session["numerodueno"] = formulario["numerodueno"]

        if "tiponegocio_alquiler" in formulario:
            session["tiponegocio_alquiler"] = True

        if "tiponegocio_venta" in formulario:
            session["tiponegocio_venta"] = True

        session["latitude_gps"] = formulario["latitude_gps"]
        session["longitude_gps"] = formulario["longitude_gps"]
        session["dueno"] = formulario["dueno"]
        session["precioventa"] = formulario["precioventa"]
        session["precioalquiler"] = formulario["precioalquiler"]
        session["totalmetros"] = formulario["totalmetros"]
        session["nombre"] = formulario["nombre"]
        session["precision"] = formulario["precision"]

    def comprobarexiste_iditem(self, iditem):
        resultado = managermongo.comprobarexiste_iditem(iditem)
        if resultado == 1:
            datos = managermongo.get_vivienda_porid(iditem)
            return self.errores.existe, datos
        elif resultado > 1:
            return self.errores.duplicado, None
            # raise Exception("id item con mas de 2 documentos {0} ".format(iditem))
        elif resultado <= 0:
            return self.errores.noexiste, None

    def actualizar_vivienda(self, formulario: dict, carpeta_subidas, max_content_length, datosmongo: list):
        try:
            length_files = int(formulario["files_len"])
            longitud_file_ya_existe = int(formulario["longitud_file_ya_existe"])
            habitaciones = int(formulario["habitaciones"])
            banyos = int(formulario["banos"])
            precioventa = int(formulario["precioventa"])
            precioalquiler = int(formulario["precioalquiler"])
            totalmetros = int(formulario["totalmetros"])

        except ValueError:
            raise Exception("no podido convertir")

        datosarchivos = []
        # procesar los archivos antiguos
        for i in range(0, longitud_file_ya_existe):
            if "file_ya_existe_{0}_nombrefile".format(i) in formulario:
                for o in range(0, length_files):
                    if (formulario["file_ya_existe_{0}_nombrefile".format(i)] == datosmongo[o]["nombrefile"]) and \
                            (formulario["file_ya_existe_{0}_nombrefile_fromform".format(i)] == datosmongo[o][
                                "nombrefile_from_form"]) and \
                            (formulario["file_ya_existe_{0}_tamano".format(i)] == datosmongo[o]["tamano_str"]):
                        datosarchivos.append(
                            {
                                "nombrefile": datosmongo[o]["nombrefile"],
                                "nombrefile_fromform": datosmongo[o]["nombrefile_from_form"],
                                "tamano": datosmongo[o]["tamano_str"]
                            })

        for i in range(0, length_files):
            if "files_{0}_datafile".format(i) in formulario:
                datafile_b64 = formulario["files_{0}_datafile".format(i)]

                if sys.getsizeof(datafile_b64) > max_content_length:
                    continue

                nombrefile_from_form = secure_filename(formulario["files_{0}_filename".format(i)])

                if datafile_b64 == "" or nombrefile_from_form == "":
                    raise Exception("campo vacio {0}".format(nombrefile_from_form))

                nombrefile = datetime.utcnow().strftime("%d-%b-%Y-%H.%M.%S.%f_") + nombrefile_from_form

                tamanoarchivo_bytes = sys.getsizeof(datafile_b64)

                self.control_archivos(carpeta_subidas, datafile_b64, datosarchivos, nombrefile, nombrefile_from_form,
                                      tamanoarchivo_bytes)

        tiponegocio_alquiler = False
        tiponegocio_venta = False
        if "tiponegocio_alquiler" in formulario:
            tiponegocio_alquiler = True

        if "tiponegocio_venta" in formulario:
            tiponegocio_venta = True

        ok = managermongo.actualizacion_producto(
            formulario["calle"],
            formulario["cp"],
            habitaciones,
            formulario["localidad"],
            formulario["numero"],
            banyos,
            formulario["wasap"],
            formulario["tipocasa"],
            formulario["telefonodueno"],
            formulario["calledueno"],
            formulario["numerodueno"],
            tiponegocio_alquiler,
            tiponegocio_venta,
            formulario["latitude_gps"],
            formulario["longitude_gps"],
            formulario["dueno"],
            precioventa,
            precioalquiler,
            totalmetros,
            formulario["usuario_que_modifica"],
            formulario["precision"],
            datosarchivos,
            formulario["iditem"]

        )

        return ok

    def getdeencodedfile(self, archivo):
        cad_cero = archivo.find(',')
        imagen_data64_core = archivo[cad_cero + 1:]
        archivo_decodificado = base64.decodebytes(imagen_data64_core.encode())
        return archivo_decodificado

    def generarmensajeerror(self, mensajeerror, anterior_calle, anterior_numero):

        if mensajeerror == self.errores.insertado_correctamente:
            return "DADO DE ALTA CORRECTAMENTE<p>Calle: {0}<br>Numero: {1}</p>".format(anterior_calle, anterior_numero)
        elif mensajeerror == self.errores.no_actualizado:
            return "ERROR - NO ACTUALIZADO"
        elif mensajeerror == self.errores.duplicado:
            return "ERROR - DOS VIVIENDAS CON LA MISMA CALLE Y EL MISMO NUMERO"
        elif mensajeerror == self.errores.actualizado_correctamente:
            return "ACTUALIZADO CORRECTAMENTE"
        else:
            return "PROBLEMA GENERAL"
