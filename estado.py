# estado.py
# Datos que comparten parser.py y los archivos de reglas de cada integrante:
# el codigo que se esta analizando, la lista de errores sintacticos y un
# contador de las construcciones que se van reconociendo (para el log).

from collections import Counter, namedtuple

codigo = ''
errores = []                 # (linea, columna, mensaje)
construcciones = Counter()   # nombre de construccion -> veces reconocida


# ------------------------------------------------------------
# Datos del analizador semantico (Avance 3)
# ------------------------------------------------------------

# tipos que el analizador semantico sabe revisar; cualquier otro (clases,
# List<Int>, Int?, ...) se trata como "desconocido" y no genera errores
BASICOS = ('Int', 'Long', 'Float', 'Double', 'String', 'Boolean', 'Char')

Simbolo = namedtuple('Simbolo', 'nombre tipo mutable ambito linea')

errores_sem = []             # (linea, categoria, mensaje)
simbolos = []                # todos los simbolos declarados (para el log)
ambitos = [{}]               # pila de ambitos; el 0 es el de archivo
params_pendientes = []       # parametros que entran al ambito del siguiente {
cierres_pendientes = 0       # } leidas cuyo ambito todavia no se cierra


class Valor(str):
    """Lo que devuelven las reglas de expresion. Se comporta como el texto de
    antes ('expr', 'id', 'miembro', 'index') pero ademas lleva su tipo."""

    def __new__(cls, etiqueta, tipo=None, literal=False, nombre=None):
        v = super().__new__(cls, etiqueta)
        v.tipo = tipo            # tipo basico o None si no se sabe
        v.literal = literal      # True si es un numero escrito en el codigo
        v.nombre = nombre        # nombre de la variable (si es un ID)
        return v


def tipo_de(valor):
    return getattr(valor, 'tipo', None)


def tipo_basico(nombre):
    return nombre if nombre in BASICOS else None


def error_sem(linea, categoria, mensaje):
    e = (linea, categoria, mensaje)
    if e not in errores_sem:
        errores_sem.append(e)


# ---------- tabla de simbolos ----------
def declarar(nombre, tipo, mutable, linea):
    s = Simbolo(nombre, tipo, mutable, len(ambitos) - 1, linea)
    ambitos[-1][nombre] = s
    simbolos.append(s)


def buscar(nombre):
    for ambito in reversed(ambitos):
        if nombre in ambito:
            return ambito[nombre]
    return None


def param_pendiente(nombre, tipo):
    params_pendientes.append((nombre, tipo))


# Los ambitos siguen a las llaves { } del flujo de tokens (ver FlujoTokens).
# El cierre se aplica cuando el parser pide el token siguiente a la }, asi las
# sentencias que estan antes de la } todavia se revisan dentro de su ambito.
def abrir_ambito(linea=0):
    ambitos.append({})
    for nombre, tipo in params_pendientes:
        declarar(nombre, tipo, False, linea)
    params_pendientes.clear()


def pedir_cierre():
    global cierres_pendientes
    cierres_pendientes += 1


def aplicar_cierres():
    global cierres_pendientes
    while cierres_pendientes > 0:
        if len(ambitos) > 1:
            ambitos.pop()
        cierres_pendientes -= 1


def reiniciar(texto):
    global codigo, cierres_pendientes
    codigo = texto
    errores.clear()
    construcciones.clear()
    errores_sem.clear()
    simbolos.clear()
    params_pendientes.clear()
    ambitos[:] = [{}]
    cierres_pendientes = 0


def registrar(nombre):
    construcciones[nombre] += 1


def columna(pos):
    inicio_linea = codigo.rfind('\n', 0, pos) + 1
    return pos - inicio_linea + 1


def error_en(linea, pos, mensaje):
    col = columna(pos)
    errores.append((linea, col,
                    f'Error sintáctico (línea {linea}, col. {col}): {mensaje}'))


# Despues de recuperarse de un error (regla con "error") se avisa a PLY para que
# el siguiente error se informe de inmediato y no se oculte por la recuperacion
def recuperar(p):
    if p.slice[1].type == 'error':
        p.parser.errok()
