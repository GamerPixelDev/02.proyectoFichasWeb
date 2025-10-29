import logging, os
from config import LOG_DIR, APP_LOG_FILE, ERROR_LOG_FILE, USER_LOG_FILE

#=== Configuración de rutas ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

#=== Rutas de los archivos de log ===
#APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")
#ERROR_LOG_FILE = os.path.join(LOG_DIR, "errors.log")
#USER_LOG_FILE = os.path.join(LOG_DIR, "user_actions.log")

#=== Formato general ===
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

#=== HANDLERS ===
#--- Mensajes generales ---
app_handler = logging.FileHandler(APP_LOG_FILE, encoding="utf-8")
app_handler.setLevel(logging.INFO)
app_handler.setFormatter(formatter)

#--- Errores ---
error_handler = logging.FileHandler(ERROR_LOG_FILE, encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

#--- Acciones del usuario ---
user_handler = logging.FileHandler(USER_LOG_FILE, encoding="utf-8")
user_handler.setLevel(logging.INFO)
user_handler.setFormatter(formatter)

#=== LOGGERS ===
#--- Logger general ---
app_logger = logging.getLogger("gestion_fichas")
app_logger.setLevel(logging.INFO)

#Para evitare duplicidades de handlers
if not app_logger.hasHandlers():
    app_logger.addHandler(app_handler)
    app_logger.addHandler(error_handler)
    #app_logger.addHandler(user_handler)

# --- Logger de errores ---
error_logger = logging.getLogger("gestion_fichas.error")
error_logger.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)
error_logger.propagate = False  # 🔒 No propaga al padre

# --- Logger de usuario ---
user_logger = logging.getLogger("gestion_fichas.user")
user_logger.setLevel(logging.INFO)
user_logger.addHandler(user_handler)
user_logger.propagate = False  # 🔒 Evita duplicación en app.log

#=== Loggers secundarios ===
error_logger = logging.getLogger("gestion_fichas.error")
user_logger = logging.getLogger("gestion_fichas.user")

#Reutilizan los mismos handlers del logger principal
error_logger.handlers = app_logger.handlers
user_logger.handlers = app_logger.handlers

"""#Nombre del archivo de log por fecha
log_filename = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")
#Configuración básica del loggin
logging.basicConfig(
    level = logging.INFO, #Nivel mínimo que se registra (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format = "%(asctime)s - %(levelname)s - %(message)s",
    handlers = [
        logging.FileHandler(log_filename, encoding = 'utf-8'),
        logging.StreamHandler() #Esto también muestra los logs en la consola
    ]
)
#Crear un logger que podremos importar desde otros archivos
logger = logging.getLogger(__name__)""" #Todo comentado porque se ha sustituido por el codigo anterior.