import json
import uuid
import os
from gestion_fichas.logger_config import app_logger
from config import DATA_DIR

# === Ruta del archivo de fichas ===
FICHAS_FILE = os.path.join(DATA_DIR, "fichas.json")

def reparar_ids_fichas():
    """
    Añade un campo 'id' único a todas las fichas que no lo tengan.
    No elimina ni modifica otros datos.
    """
    if not os.path.exists(FICHAS_FILE):
        print("❌ No se encontró el archivo fichas.json.")
        app_logger.error("Archivo fichas.json no encontrado al intentar reparar IDs.")
        return

    with open(FICHAS_FILE, "r", encoding="utf-8") as f:
        try:
            fichas = json.load(f)
        except json.JSONDecodeError:
            print("❌ Error: fichas.json está corrupto o mal formateado.")
            app_logger.error("Error JSON al leer fichas.json durante reparación.")
            return

    corregidas = 0
    for ficha in fichas:
        if "id" not in ficha or not ficha["id"]:
            ficha["id"] = str(uuid.uuid4())
            corregidas += 1

    if corregidas > 0:
        with open(FICHAS_FILE, "w", encoding="utf-8") as f:
            json.dump(fichas, f, ensure_ascii=False, indent=4)
        print(f"✅ Se añadieron IDs a {corregidas} fichas.")
        app_logger.info(f"Se añadieron IDs a {corregidas} fichas sin identificador.")
    else:
        print("✅ Todas las fichas ya tenían un ID.")
        app_logger.info("Todas las fichas ya tenían un ID válido.")

if __name__ == "__main__":
    print("🔧 Iniciando reparación de IDs en fichas...")
    reparar_ids_fichas()
    print("🔚 Reparación completada.")
