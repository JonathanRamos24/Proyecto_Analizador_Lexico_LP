# KotLex - Analizador lexico para un subconjunto de Kotlin usando PLY
# Lenguajes de Programacion
# Integrantes: Jonathan Ramos, Miguel Galarza, Willian Pacalla
#
# Uso:   python lexer.py <archivo.kt> <usuarioGit>
# Ej:    python lexer.py algoritmos/algoritmo1.kt JonathanRamos24

import os
import sys
from datetime import datetime

import ply.lex as lex


# ------------------------------------------------------------
# Inicio aporte Jonathan Ramos (JonathanRamos24)
# Palabras reservadas, identificadores y comentarios
# ------------------------------------------------------------

reserved = {
    # variables
    'val': 'VAL',
    'var': 'VAR',
    'const': 'CONST',
    # funciones y clases
    'fun': 'FUN',
    'return': 'RETURN',
    'vararg': 'VARARG',
    'class': 'CLASS',
    'object': 'OBJECT',
    # estructuras de control
    'if': 'IF',
    'else': 'ELSE',
    'when': 'WHEN',
    'for': 'FOR',
    'while': 'WHILE',
    'do': 'DO',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    # pertenencia, tipo y casting
    'in': 'IN',
    'is': 'IS',
    'as': 'AS',
    # literales especiales
    'true': 'TRUE',
    'false': 'FALSE',
    'null': 'NULL',
    # En Kotlin estas no son palabras reservadas (son funciones de la libreria
    # estandar), pero las sacamos como tokens aparte porque las usa la gramatica
    'listOf': 'LISTOF',
    'mapOf': 'MAPOF',
    'setOf': 'SETOF',
    'print': 'PRINT',
    'println': 'PRINTLN',
    'readln': 'READLN',
}

tokens = ['ID'] + list(reserved.values())


# Comentario de una linea: // hasta el final de la linea
def t_ignore_COMENTARIO_LINEA(t):
    r'//[^\n]*'
    pass


# Comentario de varias lineas. En Kotlin se pueden anidar /* /* */ */ y eso
# no se puede con una sola expresion regular, asi que se cuentan los niveles
# a mano y se mueve la posicion del lexer hasta donde cierra el comentario.
def t_ignore_COMENTARIO_BLOQUE(t):
    r'/\*'
    data = t.lexer.lexdata
    i = t.lexer.lexpos
    nivel = 1
    while i < len(data) and nivel > 0:
        if data.startswith('/*', i):
            nivel += 1
            i += 2
        elif data.startswith('*/', i):
            nivel -= 1
            i += 2
        else:
            i += 1

    if nivel > 0:
        col = find_column(data, t)
        t.lexer.errores.append(
            (t.lineno, col, '/*',
             f'Error léxico (línea {t.lineno}, col. {col}): comentario "/*" sin cerrar. Falta "*/"'))

    t.lexer.lineno += data.count('\n', t.lexpos, i)
    t.lexer.lexpos = i


# Identificadores: si el lexema esta en el diccionario es palabra reservada
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# ------------------------------------------------------------
# Fin aporte Jonathan Ramos
# ------------------------------------------------------------


# ------------------------------------------------------------
# Inicio aporte Miguel Galarza
# Operadores
# ------------------------------------------------------------

# ------------------------------------------------------------
# Fin aporte Miguel Galarza
# ------------------------------------------------------------


# ------------------------------------------------------------
# Inicio aporte Willian Pacalla
# Literales (numeros, Char, String) y delimitadores
# ------------------------------------------------------------

# ------------------------------------------------------------
# Fin aporte Willian Pacalla
# ------------------------------------------------------------


# ------------------------------------------------------------
# Parte comun: saltos de linea, espacios, errores y log
# ------------------------------------------------------------

t_ignore = ' \t\r'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def find_column(data, token):
    inicio_linea = data.rfind('\n', 0, token.lexpos) + 1
    return token.lexpos - inicio_linea + 1


def t_error(t):
    c = t.value[0]
    col = find_column(t.lexer.lexdata, t)
    msg = f'Error léxico (línea {t.lineno}, col. {col}): carácter no reconocido "{c}".'
    if c == '#':
        msg += ' Kotlin no usa "#", para comentarios use //'
    t.lexer.errores.append((t.lineno, col, c, msg))
    t.lexer.skip(1)


def analizar(codigo):
    lexer = lex.lex()
    lexer.errores = []
    lexer.input(codigo)

    resultado = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        resultado.append((tok.lineno, find_column(codigo, tok), tok.type, tok.value))
    return resultado, lexer.errores


def guardar_log(archivo, usuario, resultado, errores):
    os.makedirs('logs', exist_ok=True)
    ahora = datetime.now()
    nombre = f"logs/lexico-{usuario}-{ahora.strftime('%d-%m-%Y-%Hh%M')}.txt"

    with open(nombre, 'w', encoding='utf-8') as f:
        f.write('KotLex - Analizador lexico\n')
        f.write(f'Archivo: {archivo}\n')
        f.write(f'Usuario: {usuario}\n')
        f.write(f"Fecha:   {ahora.strftime('%d/%m/%Y %H:%M:%S')}\n\n")

        f.write(f"{'#':<5}{'Linea':<7}{'Col':<6}{'Token':<16}Lexema\n")
        for i, (linea, col, tipo, valor) in enumerate(resultado, 1):
            f.write(f'{i:<5}{linea:<7}{col:<6}{tipo:<16}{valor}\n')

        f.write(f'\nErrores ({len(errores)}):\n')
        if not errores:
            f.write('Ninguno\n')
        for e in errores:
            f.write(e[3] + '\n')

        f.write(f'\nTotal: {len(resultado)} tokens validos, {len(errores)} errores\n')
    return nombre


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: python lexer.py <archivo.kt> <usuarioGit>')
        sys.exit(1)

    archivo, usuario = sys.argv[1], sys.argv[2]
    with open(archivo, encoding='utf-8') as f:
        codigo = f.read()

    resultado, errores = analizar(codigo)
    for linea, col, tipo, valor in resultado:
        print(f'{linea}:{col}\t{tipo}\t{valor}')
    for e in errores:
        print(e[3])

    log = guardar_log(archivo, usuario, resultado, errores)
    print(f'\n{len(resultado)} tokens, {len(errores)} errores. Log guardado en {log}')
