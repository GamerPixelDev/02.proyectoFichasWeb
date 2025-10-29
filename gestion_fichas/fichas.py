import json, os
from datetime import datetime
from gestion_fichas.utils import pedir_nombre, pedir_edad, pedir_ciudad
from gestion_fichas.logger_config import app_logger, error_logger, user_logger
from config import FICHAS_FILE, DATA_DIR

#=== Configuración de rutas ===
#Carpeta base --> donde está este archivo (gestion_fichas/)
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#Carpeta 'data' --> un nivel por encima
#DATA_DIR = os.path.join(BASE_DIR, "..", "data")
#Crear la carpeta si no existe
os.makedirs(DATA_DIR, exist_ok=True)
#Ruta completa del archivo JSON
#NOMBRE_ARCHIVO = os.path.join(DATA_DIR, "fichas.json")

#=== Funciones de carga y guardado ===
def cargar_fichas(nombre_archivo = FICHAS_FILE):
    #Carga las fichas desde un archivo JSON si existe, o crea una lista vacia.
    if os.path.exists(nombre_archivo):
        try:
            with open(nombre_archivo, "r", encoding="utf-8") as f:
                fichas = json.load(f)
                app_logger.info(f"{len(fichas)} fichas cargadas correctamente desde {nombre_archivo}.")
                return fichas
        except json.JSONDecodeError:
            error_logger.error(f"El archivo {nombre_archivo} estaba dañado o vacío.")
            print(f"El archivo {nombre_archivo} está dañado o vacío. Se creará uno nuevo.")
            return []
        except Exception as e:
            error_logger.exception(f"Error al leer el archivo {nombre_archivo}: {e}")
            print(f"Error leyendo {nombre_archivo}: {e}")
            return []
    else:
        app_logger.info("Archivo fichas.json no encontrado.")
        print(f"No se encontró {nombre_archivo}. Se creará uno nuevo al cargar.")
        return []

def guardar_fichas(fichas, nombre_archivo = FICHAS_FILE):
    #Guarda la lista completa en JSON (sobreescribe).
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            json.dump(fichas, f, ensure_ascii=False, indent=4)
        app_logger.info(f"Se guardaron {len(fichas)} fichas en el archivo.")
    except Exception as e:
        error_logger.exception(f"Error al guardar la ficha: {e}")
        print(f"Error al guardar fichas: {e}")
    else:
        print(f"Fichas guardadas en {nombre_archivo} (total: {len(fichas)}).")

def crear_ficha(fichas, nombre_archivo = FICHAS_FILE):
    try:
        #Crea una nueva ficha y la añade a la lista, guardando después.
        nombre = pedir_nombre()
        edad = pedir_edad() #Devuelve un int
        ciudad = pedir_ciudad()
        fecha_now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        nueva_ficha={
            "nombre": nombre,
            "edad": edad,
            "ciudad": ciudad,
            "fecha_creacion": fecha_now,
            "fecha_modificacion": None
        }
        #Comprobamos duplicados por nombre exacto (insensible a mayúsculas)
        existentes = [f for f in fichas if f["nombre"].lower() == nombre.lower()]
        if existentes:
            print(f"Ya existe/n {len(existentes)} ficha/s con ese nombre.")
            if input("¿Crear otra igualmente? (s/n): ").strip().lower() != "s":
                user_logger.info("Se ha cancelado la creación de una ficha al haber una con el mismo nombre.")
                print("Cancelado.")
                return
        fichas.append(nueva_ficha)
        guardar_fichas(fichas, nombre_archivo)
        user_logger.info(f"Ficha creada: {nombre} / {edad} / {ciudad}")
    except Exception as e:
        error_logger.exception(f"Error al crear ficha: {e}")
        print("Error al crear la ficha.")

def mostrar_datos(fichas):
    if not fichas:
        app_logger.warning("No hay ninguna ficha creada aún.")
        print("No hay fichas registradas todavía.")
        return
    print("\n=== FICHAS REGISTRADAS ===")
    for i, ficha in enumerate(fichas, start=1):
        print(
            f"\nFicha {i}:"
            f"\nNombre: {ficha.get('nombre')}"
            f"\nEdad: {ficha.get('edad')}"
            f"\nCiudad: {ficha.get('ciudad')}"
            f"\nCreada: {ficha.get('fecha_creacion')}"
            f"\nmodificada: {ficha.get('fecha_modificacion')}"
        )
    app_logger.info("Fichas mostradas correctamente.")
    print("==========================\n")

def buscar_fichas_por_nombre(fichas, termino):
    #Búsqueda (devuelve lista de tuplas(idx, ficha))
    termino = termino.strip().lower()
    resultados = []
    for idx, f in enumerate(fichas):
        if termino in f.get("nombre", "").lower():
            resultados.append((idx, f))
    return resultados

def buscar_ficha(fichas):
    termino = input("Introduce el nombre a buscar: ").strip()
    resultados = buscar_fichas_por_nombre(fichas, termino)
    if not resultados:
        app_logger.warning("No se han encontrado coincidencias en la búsqueda.")
        print("No se encuetran coincidencias.")
        return
    app_logger.info(f"Se encontraron {len(resultados)} fichas que coinciden con la búsqueda realizada.")
    print(f"\nSe encontraron {len(resultados)} que coindice/n:")
    for i, (idx, f) in enumerate(resultados, start=1):
        print(
            f"\nFicha: {i}"
            f"\nNombre: {f['nombre']}"
            f"\nEdad: {f['edad']}"
            f"\nCiudad: {f['ciudad']}"
            f"\nCreada: {f['fecha_creacion']}"
            f"\nModificada: {f['fecha_modificacion']}"
        )

def modificar_ficha(fichas, nombre_archivo = FICHAS_FILE):
    nombre_buscado= input("Introduce el nombre de la ficha que quieras buscar/modificar: ").strip().lower()
    coincidencias = buscar_fichas_por_nombre(fichas, nombre_buscado)
    if not coincidencias:
        app_logger.info(f"No se han encontrado coincidencias para {nombre_buscado}.")
        print("No se encontraron fichas con ese nombre.")
        return
    print(f"\nSe encontraron {len(coincidencias)} coincidencia/s:\n")
    for i, (idx, f) in enumerate(coincidencias, start=1):
        print(
            f"Ficha [{i}]"
            f"\nNombre: {f.get('nombre')}"
            f"\nEdad: {f.get('edad')}"
            f"\nCiudad: {f.get('ciudad')}"
            f"\nindex: {idx}"
        )
    if len(coincidencias) > 1:
        try:
            pos = int(input(f"Elige el número de la ficha a modificar: (1 - {len(coincidencias)}): ").strip())
            if not (1 <= pos <= len(coincidencias)):
                raise ValueError("Fuera de rango.")
            sel_index = pos - 1
        except ValueError:
            error_logger.error("Se ha introducido una entrada no válida para modificar una ficha.")
            print("Entrada no válida.")
            return
    else:
        sel_index = 0
    idx_global, ficha = coincidencias[sel_index] #Índice real en la lista fichas
    while True:
        print("\nDatos actuales:")
        print(f"1. Nombre: {ficha['nombre']}")
        print(f"2. Edad: {ficha['edad']}")
        print(f"3. Ciudad: {ficha['ciudad']}")
        print(f"4. Guardar cambios y salir")
        print(f"5. Salir sin guardar.")
        eleccion = input("Elige que desea cambiar (1 - 5): ").strip()
        if eleccion == "1":
            ficha["nombre"] = pedir_nombre()
            user_logger.info(f"Nombre modificado para idx = {idx_global}.")
        elif eleccion == "2":
            ficha["edad"] = pedir_edad()
            user_logger.info(f"Edad modificada para idx = {idx_global}.")
        elif eleccion == "3":
            ficha["ciudad"] = pedir_ciudad()
            user_logger.info(f"Ciudad modificada para idx = {idx_global}.")
        elif eleccion == "4":
            ficha["fecha_modificacion"] = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            fichas[idx_global] = ficha #Se actualiza la lista principal
            guardar_fichas(fichas, nombre_archivo)
            user_logger.info(f"Ficha idx = {idx_global} guardada (modificada).")
            print("Ficha modificada y guardada.")
            return #Se puede cambiar por un return para volver al menu principal
        elif eleccion == "5":
            app_logger.info(f"Se ha cancelado y no se ha actualizado la ficha idx = {idx_global}.")
            print("Modificación cancelada, no se ha guardado nada.")
            return
        else:
            print("Opción NO válida. Inténtelo de nuevo.")

def eliminar_ficha(fichas, nombre_archivo = FICHAS_FILE):
    nombre_buscado= input("Introduce el nombre de la ficha que quieras eliminar: ").strip().lower()
    coincidencias = buscar_fichas_por_nombre(fichas, nombre_buscado)
    if not coincidencias:
        app_logger.warning(f"No se ha encontrado fichas para eliminar con {nombre_buscado}.")
        print("No se encontraron fichas con ese nombre.")
        return
    print(f"\nSe encontraron {len(coincidencias)} coincidencia/s:\n")
    for i, (idx, f) in enumerate(coincidencias, start=1):
        print(
            f"Ficha [{i}]"
            f"\nNombre: {f.get('nombre')}"
            f"\nEdad: {f.get('edad')}"
            f"\nCiudad: {f.get('ciudad')}"
            f"\nindex: {idx}"
        )
    if len(coincidencias) > 1:
        try:
            pos = int(input(f"Elige el número de la ficha a eliminar: (1 - {len(coincidencias)}): ").strip())
            if not (1 <= pos <= len(coincidencias)):
                raise ValueError("Fuera de rango.")
            sel_index = pos - 1
        except ValueError:
            error_logger.error("Selección inválida al eliminar ficha.")
            print("Entrada no válida.")
            return
    else:
        sel_index = 0
    idx_global, ficha_a_eliminar = coincidencias[sel_index]
    print(
        f"\nNombre: {ficha_a_eliminar.get('nombre')}"
        f"\nEdad: {ficha_a_eliminar.get('edad')}"
        f"\nCiudad: {ficha_a_eliminar.get('ciudad')}"
    )
    confirmar = input("Esta acción no se puede deshacer. ¿Eliminar definitivamente la ficha? (s/n): ").strip().lower()
    if confirmar == "s":
        try:
            fichas.pop(idx_global)
            guardar_fichas(fichas, nombre_archivo)
            user_logger.info(f"Ficha eliminada con idx = {idx_global}, Nombre: {ficha_a_eliminar.get('nombre')}")
            print("Ficha eliminada correctamente.")
        except Exception as e:
            error_logger.exception(f"Error eliminando la ficha idx = {idx_global}: {e}")
            print("Error al eliminar la ficha.")
    else:
        app_logger.info("Se ha cancelado la eliminación de la ficha.")
        print("Acción cancelada.")