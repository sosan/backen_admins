# -*- coding:utf-8 -*-
"""
APLICACION BACKEND INMOBILIARIA

"""

import os

# configuracion de puertos, path, etc...
import settings

from datetime import datetime

from flask import Flask, jsonify
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask import send_from_directory

from ModuloMongodb.ManagerMongodb import managermongo
# from ModuloLogica.ManagerLogica import ManagerLogica
from ModuloLogica.ManagerLogicaUsuarios import ManagerLogicaUsuarios
from ModuloLogica.ManagerLogicaComerciales import ManagerLogicaComerciales
from ModuloLogica.ManagerLogicaAdministradores import ManagerLogicaAdministradores
from ModuloHelper.ManagerHelper import Errores
from ModuloWeb.ManagerWeb import ManagerWeb
from flask_socketio import SocketIO, emit

import sys

# instanciaciones e inicializaciones
app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# instanciacion de variables
managerweb = ManagerWeb()
socketio = SocketIO(app)
bootstrap = Bootstrap(app)
errores = Errores()
# managerlogica = ManagerLogica()
managerlogica_usuarios = ManagerLogicaUsuarios()
managerlogica_comerciales = ManagerLogicaComerciales()
managerlogica_administradores = ManagerLogicaAdministradores()

# configuracion
app.secret_key = "holaa"
# CARPETAS_SUBIDAS obtenie una ruta absoluta desde "static/images/archivos_subidos"
CARPETA_SUBIDAS = os.path.abspath("static/images/archivos_subidos")
# mostramos la ruta absolta, pos si hay algun error
# TODO: implementar un logerror
print("carpeta subida archivos:" + CARPETA_SUBIDAS)

# configuracion de APP.CONFIG
app.config["CARPETA_SUBIDAS"] = CARPETA_SUBIDAS

# establecemos un limite 16 megas por archivo subido
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


###################################
# BACKEND DE ADMINISTRADORES
###################################
# TODO: controlarlo mejor
# @limiter.limit("1/second")
@app.route("/admin", methods=["GET"])
def admin_login():
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == True:
        # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
        ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])

        # en caso de que no exista borramos las variables de sesion.
        # TODO: ...
        # ..controlar mejor el acceso, si no coincide con las ultimas ips,
        # reconocimiento de usuariosa traves de escritura..
        if ok == False:
            session.clear()
            return redirect(url_for("admin_login"))
        else:
            return redirect(url_for("menu_dashboard"))

    # renderizamos el login_admin.html
    return render_template("login_admin.html")


# dividimos el metodo get y post para que en caso de usuario actualice el navegador
# con el meotod POST no redirige a "admin_login"
# de momento limitamos el 1/segundo
# TODO: controlarlo mejor
# @limiter.limit("1/second")
@app.route("/admin", methods=["POST"])
def recibir_login():
    if "usuario" and "password" in request.form:
        # deberiamos hacer esta comprobacion con un base de datos mucho mas rapida que mysql
        # por ejemplo: mongodb o redis.
        # en este caso para no complicarlo demasiado hacemos la comprobacion contra mysql
        ok, datos = managerlogica_administradores.comprobar_existencia_admin(usuario=request.form["usuario"],
                                                                             password=request.form["password"])
        # nos han devuelto: ok => si no ha habido algun erro y el nombre del usuario
        if ok == True:
            # el usuario y password los guardamos en una sesion para consultarlo
            # mas adelante y en proximas conexiones que haga el usuario.
            # ademas tambien guardamos el nombre de usuario y asi nos ahorramos
            # tener que volver a consultar a la base de datos
            session["usuario"] = request.form["usuario"]
            session["password"] = request.form["password"]
            session["nombre"] = datos["nombre"]
            session["imagen_perfil"] = datos["imagen_perfil"]
            # redirigimos al menu de administradores para que haga un render del html
            # podriamos hacer un render desde aqui
            # pero en caso de que el usuario actulice el navegador, saltaria un error
            return redirect(url_for("menu_dashboard"))
        else:
            # TODO: faltaria controlar los errores de login
            # con base de datos, recogiendo la ip, etc...
            # tambien controlamos redirigirlo a la pagina principal, etc...
            return redirect(url_for("admin_login"))

    # directamente si nos hacen una peticion donde no haya un usuaro y password,
    # redigimos a "admin_login"
    # actualmente controlamos el limite de peticiones rate-limiter de flask, pero podriamos
    # controlar mucho mejor el tiempo de peticiones, ips, ataques, etc...
    # TODO: mejorar el control de peticiones
    return redirect(url_for("admin_login"))


@app.route("/dashboard", methods=["GET"])
def menu_dashboard():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])

    # en caso de que no exista borramos las variables de sesion.
    # TODO: ...
    # ..controlar mejor el acceso, si no coincide con las ultimas ips, reconocimiento de usuariosa traves de escritura..
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))
    fecha_inicio, fecha_fin = managerlogica_administradores.obtener_ultimasdias(6)

    return render_template("menu_dashboard.html",
                           nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"],
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin,
                           isactive_dashboard=True
                           )


@app.route("/estadisticas", methods=["GET"])
def menu_estadisticas():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    # en caso de que no exista borramos las variables de sesion.
    # TODO: ...
    # ..controlar mejor el acceso, si no coincide con las ultimas ips, reconocimiento de usuariosa traves de escritura..
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    fecha_inicio, fecha_fin = managerlogica_administradores.obtener_ultimasdias(6)

    return render_template("menu_estadisticas.html",
                           nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"],
                           fecha_inicio=fecha_inicio,
                           fecha_fin=fecha_fin,
                           isactive_estadistica=True
                           )


@app.route("/editar_administrators", methods=["GET"])
def listar_administradores():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    # en caso de que no exista borramos las variables de sesion.
    # TODO: ...
    # ..controlar mejor el acceso, si no coincide con las ultimas ips, reconocimiento de usuariosa traves de escritura..
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    return render_template("editar_administradores.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"])


@app.route("/nuevo_administrators", methods=["GET"])
def nuevo_administrador():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    # en caso de que no exista borramos las variables de sesion.
    # TODO: ...
    # ..controlar mejor el acceso, si no coincide con las ultimas ips, reconocimiento de usuariosa traves de escritura..
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    # comprobamos que el usuario y session actual tengan los privilegios para crear un nuevo administrador
    # permisos para crear un nuevo admin = 1
    tiene_permiso = managerlogica_administradores.comprobar_permisos_admin(session["usuario"], 1)
    if tiene_permiso == False:
        # TODO: faltaria que saltara alguna alarma, notificion, que se ha intentado crear un usuario sin tener permisos
        session.clear()
        return redirect(url_for("admin_login"))

    if "mensajeerror" in session:
        mensajeerror = session.pop("mensajeerror")
        return render_template("nuevo_administradores.html", nombre=session["nombre"],
                               imagen_perfil=session["imagen_perfil"], resultado_insercion=mensajeerror,
                               isactive_nuevo_administrador=True
                               )

    return render_template("nuevo_administradores.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_nuevo_administrador=True)


# esta comentado que limitemos las peticiones de 2 veces al dia
# @limiter.limit("2/day")
@app.route("/nuevo_administrators", methods=["POST"])
def recibir_datos_nuevo_administrador():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    # comprobamos que el usuario y session actual tengan los privilegios para crear un nuevo administrador
    # permisos para crear un nuevo admin = 1
    tiene_permiso = managerlogica_administradores.comprobar_permisos_admin(session["usuario"], 1)
    if tiene_permiso == False:
        # TODO: faltaria que saltara alguna alarma, notificion, que se ha intentado crear un usuario sin tener permisos
        session.clear()
        return redirect(url_for("admin_login"))

    # si nombre, apellidos,email, telef estan dentro del formulario.
    # todos los campos vienen desde formulario "nuevo_administradores.html"
    if "nombre" in request.form and \
            "apellidos" in request.form and \
            "email" in request.form and \
            "telf" in request.form and \
            "usuario" in request.form and \
            "password" in request.form:
        insertado_ok = managerlogica_administradores.insertar_administrador(request.form)
        if insertado_ok == True:
            session["mensajeerror"] = "Insertado correctamente"
        else:
            session["mensajeerror"] = "Error en la insercion"

    return redirect(url_for("nuevo_administrador"))


# -----------------------------
@app.route("/administradores_todos", methods=["GET"])
def listar_todos_administradores():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    administradores = managerlogica_administradores.obtener_todos_administradores()

    # si tenemos un mensaje de erormensaje de error
    # lo enseñamos
    mensajeerror = None
    if "mensajeerror" in session:
        # el mensaje de error lo quitamos de la session
        # y ademas los asignamos a la variable mensajeerror
        mensajeerror = session.pop("mensajeerror")

    return render_template("ver_administradores.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_editar_administrador=True,
                           datos_administradores=administradores, mensajeerror=mensajeerror
                           )


@app.route("/opciones_modificar_administradores", methods=["GET"])
def opciones_administradores():
    return redirect(url_for("listar_todos_administradores"))


@app.route("/opciones_modificar_administradores", methods=["POST"])
def opciones_modificar_administradores():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    if "modificar" in request.form:
        modificado_correcto = managerlogica_administradores.modificar_administrador(request.form)
        if modificado_correcto == True:
            session["mensajeerror"] = "Modificado correctamente"
        else:
            session["mensajeerror"] = "Error de modificado"

        return redirect(url_for("listar_todos_administradores"))

    if "borrar" in request.form:
        borrado_correctamente = managerlogica_administradores.borrar_administrador(request.form["borrar"])
        if borrado_correctamente == True:
            session["mensajeerror"] = "Borrado correctamente"
        else:
            session["mensajeerror"] = "Error de borrado"

    return redirect(url_for("listar_todos_administradores"))


@app.route("/perfil_admin", methods=["GET"])
def ver_perfil_admin():
    return render_template("ver_perfil.html")


# --------------------------


@app.route("/listado_comerciales", methods=["GET"])
def listar_comerciales():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    comerciales = managerlogica_administradores.obtener_todos_comerciales()

    # si tenemos un mensaje de erormensaje de error
    # lo enseñamos
    mensajeerror = None
    if "mensajeerror" in session:
        # el mensaje de error lo quitamos de la session
        # y ademas los asignamos a la variable mensajeerror
        mensajeerror = session.pop("mensajeerror")

    return render_template("ver_comerciales.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_editar_comerciales=True,
                           datos_comerciales=comerciales, mensajeerror=mensajeerror
                           )


@app.route("/opciones_modificar_comerciales", methods=["GET"])
def opciones_comerciales():
    return redirect(url_for("listar_comerciales"))


@app.route("/opciones_modificar_comerciales", methods=["POST"])
def opciones_modificar_comerciales():
    # comprobamos que existan datos de session, si no existen vovlemos a la pagina de login
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    # comprobar el usuario y password en la session
    # TODO: para no saturar la base de datos podriamos consultar con una base de datos mongo
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    if "modificar" in request.form:
        modificado_correcto = managerlogica_administradores.modificar_comercial(request.form)
        if modificado_correcto == True:
            session["mensajeerror"] = "Modificado correctamente"
        else:
            session["mensajeerror"] = "Error de modificado"

        return redirect(url_for("listar_comerciales"))

    if "borrar" in request.form:
        borrado_correctamente = managerlogica_administradores.borrar_comercial(request.form["borrar"])
        if borrado_correctamente == True:
            session["mensajeerror"] = "Borrado correctamente"
        else:
            session["mensajeerror"] = "Error de borrado"

    return redirect(url_for("listar_comerciales"))


@app.route("/modificar_comercial", methods=["GET"])
def modificar_comercial_get():
    return redirect(url_for("listar_comerciales"))


@app.route("/nuevo_comercial", methods=["GET"])
def nuevo_comercial():
    resultado_ok = comprobar_existencia_datos_session()
    if resultado_ok == False:
        return redirect(url_for("admin_login"))

    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    if "mensajeerror" in session:
        mensajeerror = session.pop("mensajeerror")
        return render_template("nuevo_comercial.html", nombre=session["nombre"],
                               imagen_perfil=session["imagen_perfil"], resultado_insercion=mensajeerror,
                               isactive_nuevo_comercial=True
                               )

    return render_template("nuevo_comercial.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_nuevo_comercial=True)


@app.route("/nuevo_comercial", methods=["POST"])
def recibir_datos_nuevo_comercial():
    ok = managerlogica_administradores.existe_admin(session["usuario"], session["password"])
    if ok == False:
        session.clear()
        return redirect(url_for("admin_login"))

    # si nombre, apellidos,email, telef estan dentro del formulario.
    # todos los campos vienen desde formulario "nuevo_administradores.html"
    if "nombre" in request.form and \
            "apellidos" in request.form and \
            "email" in request.form and \
            "telf" in request.form and \
            "usuario" in request.form and \
            "password" in request.form:
        insertado_ok = managerlogica_administradores.insertar_comercial(request.form)
        if insertado_ok == True:
            session["mensajeerror"] = "Insertado correctamente"
        else:
            session["mensajeerror"] = "Error en la insercion"
    return redirect(url_for("nuevo_comercial"))


@app.route("/opcion2", methods=["GET"])
def opcion2():
    return render_template("menu_estadisticas.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_opcion_2=True)


@app.route("/opcion3", methods=["GET"])
def opcion3():
    return render_template("menu_estadisticas.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_opcion_3=True)


@app.route("/opcion4", methods=["GET"])
def opcion4():
    return render_template("menu_estadisticas.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_opcion_4=True)


@app.route("/opcion5", methods=["GET"])
def opcion5():
    return render_template("menu_estadisticas.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_opcion_5=True)


@app.route("/opcion6", methods=["GET"])
def opcion6():
    return render_template("menu_estadisticas.html", nombre=session["nombre"],
                           imagen_perfil=session["imagen_perfil"], isactive_opcion_6=True)


@app.route("/logout", methods=["GET"])
def logout_admin():
    session.clear()
    return redirect(url_for("admin_login"))


def comprobar_existencia_datos_session():
    # comprobar el usuario y password en la session
    if not ("usuario" in session) or not ("password" in session):
        return False

    # comprobamos que no esten vacios
    if not session["usuario"] or not session["password"]:
        return False

    return True


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    settings.readconfig()

    env_port = int(os.getenv("PORT", 5010))
    env_debug = os.getenv("FLASK_DEBUG", True)

    socketio.run(host="0.0.0.0", port=env_port, app=app, debug=env_debug)
