import os, json, uuid, secrets, hashlib, hmac
from datetime import datetime, timedelta
from gestion_fichas.logger_config import app_logger, error_logger, user_logger
from config import USUARIOS_FILE, DEFAULT_ROLE, ADMIN_ROLE

#Rutas
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#DATA_DIR = os.path.join(BASE_DIR, "..", "data")
#os.makedirs(DATA_DIR, exist_ok=True)
#USUARIOS_FILE = os.path.join(DATA_DIR, "usuarios.json")

#Configuración de hashing
HASH_NAME = "sha256"
ITERATIONS = 200_000
SALT_SIZE = 16 #bytes
TOKEN_EXPIRATION_HOURS = 12 #duración de la sesión (ajustable)

#=== Utilidades de hashing ===
def _generar_salt():
    return secrets.token_bytes(SALT_SIZE)

def _hash_password(password: str, salt:bytes) -> str:
    #Devuelve hex string del hash pbkdf2
    pw = password.encode("utf-8")
    dk = hashlib.pbkdf2_hmac(HASH_NAME, pw, salt, ITERATIONS)
    return dk.hex()

def _verificar_password(password: str, salt: bytes, stored_hash_hex: str) -> bool:
    candidate = _hash_password(password, salt)
    #compare_digest para evitar timing attacks
    return hmac.compare_digest(candidate, stored_hash_hex)

#=== IO usuarios ===
def cargar_usuarios():
    if not os.path.exists(USUARIOS_FILE):
        return []
    try:
        with open(USUARIOS_FILE, "r", encoding = "utf-8") as f:
            return json.load(f)
    except Exception as e:
        error_logger.exception(f"Error cargando usuarios: {e}")
        return []

def guardar_usuarios(usuarios):
    try:
        with open(USUARIOS_FILE, "w", encoding = "utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent = 4)
        app_logger.info(f"Guardados {len(usuarios)} usuarios.")
    except Exception as e:
        error_logger.exception(f"Error guardando usuarios: {e}")

#=== Funciones Principales ===
def _buscar_por_username(usuarios, username:str):
    username = username.strip().lower()
    for u in usuarios:
        if u["username"].lower() == username:
            return u
    return None

def registrar_usuario(username: str, password: str, role: str = "editor") -> dict:
    #Crea un usuario nuevo. Devuelve el usuario creado (sin password claro) o lanza ValueError
    usuarios = cargar_usuarios()
    if _buscar_por_username(usuarios, username):
        raise ValueError("El nombre del usuario ya existe.")
    salt = _generar_salt()
    hash_hex = _hash_password(password, salt)
    user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "salt": salt.hex(), #Almacenamos salt en hex para serializar
        "password_hash": hash_hex,
        "role": role,
        "created_at":datetime.now().isoformat()
    }
    usuarios.append(user)
    guardar_usuarios(usuarios)
    user_logger.info(f"Usuario registrado: {username} (role={role})")
    return {k: v for k, v in user.items() if k not in ("salt", "password_hash")}

_SESSIONS = {} #Sessions in memory: token -> {user_id, expires_at}

def autenticar_usuario(username: str, password: str):
    """Comprueba credenciales y devuelve (usuario_publico, token) si son válidas."""
    usuarios = cargar_usuarios()
    user = _buscar_por_username(usuarios, username)
    if not user:
        return None
    salt = bytes.fromhex(user["salt"])
    if not _verificar_password(password, salt, user["password_hash"]):
        return None
    #Generar token y guardar sesion en memoria
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours = TOKEN_EXPIRATION_HOURS)
    _SESSIONS[token] = {"user_id": user["id"], "expires_at": expires_at}
    user_logger.info(f"Usuario autenticado: {username}")
    #Devolvemos token y datos públicos del usuario
    public = {k: v for k, v in user.items() if k not in ("salt", "password_hash")}
    return public, token

def verificar_token(token: str):
    #Devuelve user public si token válido, sino None
    ses = _SESSIONS.get(token)
    if not ses:
        return None
    if ses["expires_at"] < datetime.now():
        del _SESSIONS[token] #Borra la sesión expirada
        return None
    usuarios = cargar_usuarios() #Cargamos usuario
    for u in usuarios:
        if u["id"] == ses["user_id"]:
            return {k: v for k, v in u.items() if k not in ("salt", "password_hash")}
    return None

def logout(token: str):
    #Se elimina la sesión en memoria (logout)
    if token in _SESSIONS:
        del _SESSIONS[token]
        user_logger.info(f"Logout session token = {token}")
        return True
    return False

def cambiar_pass_propio(username: str, old_password: str, new_password: str) -> bool:
    """Permite que un usuario cambie su propia contraseña."""
    usuarios = cargar_usuarios()
    user = _buscar_por_username(usuarios, username)
    if not user:
        return False
    salt = bytes.fromhex(user["salt"])
    if not _verificar_password(old_password, salt, user["password_hash"]):
        return False
    new_salt = _generar_salt()
    user["salt"] = new_salt.hex()
    user["password_hash"] = _hash_password(new_password, new_salt)
    guardar_usuarios(usuarios)
    user_logger.info(f"Usuario {username} cambió su contraseña.")
    return True

def verificar_o_crear_admin_inicial():
    #Comprobar si hay usuarios. Si no, crear admin inicial.
    if not os.path.exists(USUARIOS_FILE) or os.path.getsize(USUARIOS_FILE) == 0:
        print("\n=== No se han encontrado usuarios. Creando usuario administrador inicial===\n")
        username = input("Elige un nombre de usuario administrador: ").strip()
        password = input("Contraseña (mínimo 6 caracteres): ").strip()
        if len(password) < 6:
            print("La contraseña es demasiado corta. Inténtalo de nuevo.")
            return        
        salt = _generar_salt()
        hash_hex = _hash_password(password, salt)
        admin = {
            "id": str(uuid.uuid4()),
            "username": username,
            "salt": salt.hex(),
            "password_hash": hash_hex,
            "role": "admin",
            "created_at": datetime.now().isoformat()
            }
        with open(USUARIOS_FILE, "w", encoding="utf-8") as f:
            json.dump([admin], f, ensure_ascii=False, indent=4)
        print(f"Usuario administrador '{username}' creado con éxito.")
        user_logger.info(f"Usuario administrador inicial creado: {username}")
        return admin
    else:
        return None
    
#=== Funciones admin ===
def ver_usuarios_admin(current_user):
    if current_user.get("role") != ADMIN_ROLE:
        print("Permiso denegado. Solo administradores.")
        return
    usuarios = cargar_usuarios()
    print("\n=== LISTA DE USUARIOS ===")
    for u in usuarios:
        print(f"- {u['username']} (rol: {u.get('role', 'editor')}, creado: {u['created_at']})")
    user_logger.info(f"Administrador {current_user['username']} vio la lista de usuarios.")

def crear_usuario_admin(current_user):
    if current_user.get("role") != ADMIN_ROLE:
        print("Permiso denegado. Solo administradores.")
        return False
    username = input("Elige un nombre de usuario para el nuevo usuario: ").strip()
    password = input("Elige una contraseña para el nuevo usuario: ").strip()
    role = input("Elige un rol para el nuevo usuario (admin/editor): ").strip().lower()
    if role not in [ADMIN_ROLE, DEFAULT_ROLE]:
        print("Rol no válido.")
        return False
    try:
        registrar_usuario(username, password, role)
        user_logger.info(f"Administrador {current_user['username']} creó el usuario {username} con rol {role}.")
        print(f"Usuario creado correctamente.")
        return True
    except ValueError as v:
        print(f"No se pudo crear el usuario: {v}")
        return False

def eliminar_usuario_admin(current_user):
    if current_user.get("role") != ADMIN_ROLE:
        print("Permiso denegado. Solo administradores.")
        return False
    usuarios = cargar_usuarios()
    username = input("Introduce el nombre del usuario que quieres eliminar: ").strip()
    if username == current_user["username"]:
        print("No puedes eliminar tu propio usuario.")
        return False
    user = _buscar_por_username(usuarios, username)
    if not user:
        print("Ese usuario no existe.")
        return False
    confirmar = input(f"¿Estás seguro de que quieres eliminar al usuario {username}? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Operación cancelada.")
        return False
    usuarios.remove(user)
    guardar_usuarios(usuarios)
    user_logger.info(f"El administrador {current_user['username']} eliminó al usuario {username}.")
    print(f"Usuario {username} eliminado con éxito.")
    return True

def cambiar_rol_admin(current_user):
    if current_user.get("role") != ADMIN_ROLE:
        print("Permiso denegado. Solo administradores.")
        return False
    usuarios = cargar_usuarios()
    username = input("Introduce el nombre del usuario al que quieres cambiar el rol: ").strip()
    user = _buscar_por_username(usuarios, username)
    if not user:
        print("Ese usuario no existe.")
        return False
    nuevo = input("Nuevo rol (admin o editor): ").strip().lower()
    if nuevo not in [ADMIN_ROLE, DEFAULT_ROLE]:
        print("Rol no válido")
        return False
    user["role"] = nuevo
    guardar_usuarios(usuarios)
    user_logger.info(f"El administrador {current_user['username']} cambió el rol de {username} a {nuevo}")
    print(f"Rol de {username} actualizado a {nuevo}.")
    return True

def cambiar_pass_usuario_admin(username: str, new_password: str) -> bool:
    """Permite a un administrador cambiar la contraseña de otro usuario."""
    usuarios = cargar_usuarios()
    user = _buscar_por_username(usuarios, username)
    if not user:
        return False
    new_salt = _generar_salt()
    user["salt"] = new_salt.hex()
    user["password_hash"] = _hash_password(new_password, new_salt)
    guardar_usuarios(usuarios)
    user_logger.info(f"Contraseña de {username} actualizada por un administrador.")
    return True
