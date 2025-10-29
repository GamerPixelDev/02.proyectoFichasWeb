from flask import Flask
from webapp.routes import main_routes
import os

def create_app():
    #Ruta absoluta a la carpeta templates dentro de webapp
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    app = Flask(__name__, template_folder = templates_dir)
    app.secret_key = "super_seceret_key" # Cambiar por una clave segura luego
    #Importar rutas
    app.register_blueprint(main_routes)
    return app