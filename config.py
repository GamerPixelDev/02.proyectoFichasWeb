import os

#=== Ruta base del proyecto ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#=== Rutas de carpeta de datos
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")
GESTION_DIR = os.path.join(BASE_DIR, "gestion_fichas")

#=== Rutas de archivos JSON
USUARIOS_FILE = os.path.join(DATA_DIR, "usuarios.json")
FICHAS_FILE = os.path.join(DATA_DIR, "fichas.json")
SESSION_FILE = os.path.join(DATA_DIR, "session.json")

#=== Rutas de archivos de logs
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
USER_LOG_FILE = os.path.join(LOG_DIR, "user.log")

#=== COnfiguraciones generales ===
DEFAULT_ROLE = "editor"
ADMIN_ROLE = "admin"

#=== Configuraciones de sesión ===
SESSION_TIMEOUT_MINUTES = 30

#Asegurarse que la carpeta de datos existe
os.makedirs(DATA_DIR, exist_ok=True)