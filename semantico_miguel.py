# semantico_miguel.py
# ------------------------------------------------------------
# Inicio aporte Miguel Galarza (magselpad) - Avance 3, analizador semantico
#
#   Regla 1 - Operaciones permitidas:
#       las operaciones aritmeticas (+ - * / %, signo, ++ y --) solo se aplican
#       entre numeros (el + tambien acepta String a la izquierda) y los
#       conectores && y || solo entre Boolean.
#   Regla 2 - Conversion:
#       no hay conversion implicita entre tipos; hay que usar toInt(),
#       toDouble(), etc. Se revisa en val, var, const val y en asignaciones.
#
# Las reglas sintacticas (reglas_miguel.py y las de los demás) llaman a las
# funciones de este archivo. Los errores se guardan con estado.error_sem().
# ------------------------------------------------------------
import estado
from estado import Valor, tipo_de, error_sem

NUMERICOS = ('Int', 'Long', 'Float', 'Double')   # de menor a mayor rango

CAT_OPERACIONES = 'Operaciones permitidas'
CAT_CONVERSION = 'Conversión'

# tipo que devuelven las conversiones explicitas: texto.toInt()
CONVERSIONES = {'toInt': 'Int', 'toLong': 'Long', 'toFloat': 'Float',
                'toDouble': 'Double', 'toString': 'String'}


def _y(tipo):
    # "entre String e Int" / "entre String y Double"
    return 'e' if tipo.startswith('I') else 'y'


# ---------- Regla 1: operaciones permitidas ----------

# izq op der  con op en + - * / %
# devuelve el tipo del resultado (o None si no se sabe)
def tipo_aritmetico(op, izq, der, linea):
    a, b = tipo_de(izq), tipo_de(der)
    if op == '+' and a == 'String':
        return 'String'                      # "texto" + cualquier cosa
    if a is None or b is None or 'Char' in (a, b):
        return None                          # no se sabe: no se marca error
    if a in NUMERICOS and b in NUMERICOS:
        return max(a, b, key=NUMERICOS.index)
    error_sem(linea, CAT_OPERACIONES,
              f'no se puede aplicar "{op}" entre {a} {_y(b)} {b}.')
    return None


# signo (-x, +x) y ++ / --: el operando debe ser numerico
def tipo_unario(op, valor, linea):
    t = tipo_de(valor)
    if t is None or t == 'Char' or t in NUMERICOS:
        return t
    error_sem(linea, CAT_OPERACIONES,
              f'no se puede aplicar "{op}" a un {t}.')
    return None


# a && b     a || b
def verificar_logico(op, izq, der, linea):
    a, b = tipo_de(izq), tipo_de(der)
    if a is not None and b is not None:
        if a != 'Boolean' or b != 'Boolean':
            error_sem(linea, CAT_OPERACIONES,
                      f'no se puede aplicar "{op}" entre {a} {_y(b)} {b}.')
    else:
        conocido = a or b
        if conocido is not None and conocido != 'Boolean':
            error_sem(linea, CAT_OPERACIONES,
                      f'"{op}" solo se aplica entre Boolean, no con {conocido}.')


# ---------- Regla 2: conversion ----------

# esperado: tipo declarado (val precio: Double)   valor: la expresion asignada
def verificar_conversion(esperado, valor, linea):
    e = estado.tipo_basico(esperado)
    a = tipo_de(valor)
    if e is None or a is None or e == a:
        return
    if e == 'Long' and a == 'Int' and getattr(valor, 'literal', False):
        return                               # val grande: Long = 5  si se puede
    msg = f'se esperaba {e} pero se recibió {a}.'
    if e in NUMERICOS and a in NUMERICOS:
        msg += f' Use to{e}() para convertir.'
    error_sem(linea, CAT_CONVERSION, msg)


# val / var / const val: revisa la conversion y guarda la variable en la tabla
#   tipo_declarado: el tipo escrito (o None si no lo hay)   valor: expresion o None
def declarar_variable(nombre, tipo_declarado, valor, mutable, linea):
    if tipo_declarado is not None and valor is not None:
        verificar_conversion(tipo_declarado, valor, linea)
    if tipo_declarado is not None:
        tipo = tipo_declarado
    else:
        tipo = tipo_de(valor)                # inferencia: val x = 5  ->  Int
    estado.declarar(nombre, tipo, mutable, linea)


# x = valor      x += valor   (solo si x es una variable con tipo conocido)
def verificar_asignacion(destino, op, valor, linea):
    t = tipo_de(destino)
    if destino != 'id' or t is None:
        return
    if op == '=':
        verificar_conversion(t, valor, linea)
        return
    resultado = tipo_aritmetico(op[0], destino, valor, linea)
    if resultado is not None:
        verificar_conversion(t, Valor('expr', resultado), linea)

# ------------------------------------------------------------
# Fin aporte Miguel Galarza
# ------------------------------------------------------------
