from datetime import datetime

#Funciones
def pedir_nombre():
    nombre = input ("Introduce tu nombre: ").strip()
    #Para asegurar que un humano introduce un nombre con caracteres.
    while nombre.isdigit() or nombre == "":
        print("Has escrito un número en vez de un nombre o no has escrito nada.")
        nombre = input("Introduce tu nombre: ").strip()
    return nombre

def pedir_edad():
    edad = input ("Introduce tu edad: ").strip()
    #Nos aseguramos que un humano ha introducido un número válido para su edad.
    while not edad.isdigit() or int(edad) <= 0:
        print("No has introducido un número válido.")
        edad = input ("Introduce tu edad: ").strip()
    #Con nombre y ciudad no hace falta hacer esto porque ya se guarda como una cadena de caracteres.
    edad = int (edad)
    return edad  

def pedir_ciudad():
    ciudad = input ("Introduce tu ciudad: ").strip()
    #Nos asegururamos que un humano ha introducido un nombre válido y no un número.
    while ciudad.isdigit() or ciudad == "":
        print("Has escrito un número en vez de una ciudad o no has escrito nada.")
        ciudad = input("Introduce tu ciudad: ").strip()
    return ciudad

def obtener_fecha():
    return datetime.now().strftime("%Y/%m/%d %H:%M:%S")