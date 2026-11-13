# estado.py
# Datos que comparten parser.py y los archivos de reglas de cada integrante:
# el codigo que se esta analizando, la lista de errores sintacticos y un
# contador de las construcciones que se van reconociendo (para el log).

from collections import Counter

codigo = ''
errores = []                 # (linea, columna, mensaje)
construcciones = Counter()   # nombre de construccion -> veces reconocida


def reiniciar(texto):
    global codigo
    codigo = texto
    errores.clear()
    construcciones.clear()


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
