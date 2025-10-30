from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from gestion_fichas.usuarios import autenticar_usuario, cargar_usuarios
from gestion_fichas.fichas import cargar_fichas
from gestion_fichas.session_manager import cerrar_sesion
from gestion_fichas.logger_config import app_logger, user_logger

main_routes = Blueprint('main_routes', __name__)

# === RUTA LOGIN ===
@main_routes.route('/', methods=['GET', 'POST'])
@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        try:
            user, token = autenticar_usuario(username, password)
            if user:
                session['usuario'] = user['username']
                session['rol'] = user['role']
                session['token'] = token
                user_logger.info(f"Usuario '{username}' ha iniciado sesión.")
                flash(f"Bienvenido, {username}!", "success")
                return redirect(url_for('main_routes.dashboard'))
            else:
                flash("Credenciales inválidas. Inténtalo de nuevo.", "danger")
                user_logger.warning(f"Intento fallido de inicio de sesión para usuario '{username}'.")
        except Exception as e:
            app_logger.error(f"Error durante el inicio de sesión: {e}")
            flash("Ocurrió un error. Por favor, inténtalo más tarde.", "danger")
    return render_template('login.html')

# === RUTA DASHBOARD ===
@main_routes.route('/dashboard')
def dashboard():
    if "usuario" not in session:
        flash("Por favor, inicia sesión para acceder al dashboard.", "warning")
        return redirect(url_for('main_routes.login'))
    username = session["usuario"]
    rol = session.get("rol", "editor")
    return render_template('dashboard.html', username=username, role=rol)

# === GESTIÓN DE USUARIOS (SOLO ADMIN) ===
@main_routes.route('/usuarios')
def gestion_usuarios():
    if "usuario" not in session:
        flash("Por favor, inicia sesión para acceder a la gestión de usuarios.", "warning")
        return redirect(url_for('main_routes.login'))
    if session.get("rol") != "admin":
        flash("No tienes permisos para acceder a esta sección.", "danger")
        return redirect(url_for('main_routes.dashboard'))
    usuarios = cargar_usuarios()
    username = session["usuario"]
    rol = session.get("rol", "editor")
    return render_template('usuarios.html', username=username, role=rol, usuarios=usuarios)

# === GESTIÓN DE FICHAS ===
@main_routes.route('/fichas')
def gestion_fichas():
    if "usuario" not in session:
        flash("Por favor, inicia sesión para acceder a la gestión de fichas.", "warning")
        return redirect(url_for('main_routes.login'))
    fichas = cargar_fichas()
    username = session["usuario"]
    rol = session.get("rol", "editor")
    return render_template('fichas.html', username=username, role=rol, fichas=fichas)

# === CERRAR SESIÓN ===
@main_routes.route('/logout')
def logout():
    user = session.get("usuario", "Desconocido")
    cerrar_sesion()
    session.clear()
    flash("Has cerrado sesión exitosamente.", "info")
    user_logger.info(f"Usuario '{user}' ha cerrado sesión.")
    return redirect(url_for('main_routes.login'))

# === OTRAS RUTAS DE GESTIÓN DE USUARIOS (AGREGAR, EDITAR, ELIMINAR) ===
@main_routes.route("/usuarios/editar/<id>")
def editar_usuario(id):
    if "user" not in session:
        flash("Por favor, inicia sesión para acceder a esta función.", "warning")
        return redirect(url_for("main_routes.login"))
    flash(f"Función de editar usuario {id} aún no implementada.", "info")
    return redirect(url_for("main_routes.gestion_usuarios"))

@main_routes.route("/usuarios/eliminar/<id>")
def eliminar_usuario(id):
    if "user" not in session:
        flash("Por favor, inicia sesión para acceder a esta función.", "warning")
        return redirect(url_for("main_routes.login"))
    flash(f"Función de eliminar usuario {id} aún no implementada.", "info")
    return redirect(url_for("main_routes.gestion_usuarios"))

# === OTRAS RUTAS DE GESTIÓN DE FICHAS (AGREGAR, EDITAR, ELIMINAR) ===
@main_routes.route("/fichas/editar/<id>")
def editar_ficha(id):
    if "user" not in session:
        flash("Por favor, inicia sesión para acceder a esta función.", "warning")
        return redirect(url_for("main_routes.login"))
    flash(f"Función de editar ficha {id} aún no implementada.", "info")
    return redirect(url_for("main_routes.gestion_fichas"))

@main_routes.route("/fichas/eliminar/<id>")
def eliminar_ficha(id):
    if "user" not in session:
        flash("Por favor, inicia sesión para acceder a esta función.", "warning")
        return redirect(url_for("main_routes.login"))
    flash(f"Función de eliminar ficha {id} aún no implementada.", "info")
    return redirect(url_for("main_routes.gestion_fichas"))