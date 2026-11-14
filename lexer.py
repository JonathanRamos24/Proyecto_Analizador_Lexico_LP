# KotLex - Analizador lexico para un subconjunto de Kotlin usando PLY
# Lenguajes de Programacion
# Integrantes: Jonathan Ramos, Miguel Galarza, William Pacalla
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
    # infija que usa mapOf("a" to 1) (mejora Avance 2)
    'to': 'TO',
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
# Inicio aporte Miguel Galarza (magselpad)
# Operadores
# ------------------------------------------------------------

tokens_operadores = [
    # aritmeticos
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'INC', 'DEC',
    # asignacion
    'ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN',
    'DIV_ASSIGN', 'MOD_ASSIGN',
    # comparacion
    'EQ', 'NE', 'LT', 'GT', 'LE', 'GE',
    # logicos
    'AND', 'OR', 'NOT',
    # rango y pertenencia (in e is ya son palabras reservadas)
    'RANGE', 'NOT_IN', 'NOT_IS',
    # nulos
    'SAFE_CALL', 'ELVIS', 'NOT_NULL', 'QUESTION',
]

# se agregan a la lista de tokens que arranco Jonathan
tokens += tokens_operadores


# !in y !is se definen como funcion para que se revisen antes que '!'
# (las funciones se evaluan primero que las reglas de tipo string).
# El \b evita que "!inicio" se lea como "!in" + "icio".
def t_NOT_IN(t):
    r'!in\b'
    return t


def t_NOT_IS(t):
    r'!is\b'
    return t


# PLY ordena las reglas string de la expresion regular mas larga a la mas
# corta, por eso '++' se prueba antes que '+', '!!' antes que '!', etc.

# Aritmeticos: suma, resta, multiplicacion, division, residuo
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_INC = r'\+\+'        # incremento
t_DEC = r'--'           # decremento

# Asignacion
t_ASSIGN = r'='
t_PLUS_ASSIGN = r'\+='
t_MINUS_ASSIGN = r'-='
t_TIMES_ASSIGN = r'\*='
t_DIV_ASSIGN = r'/='
t_MOD_ASSIGN = r'%='

# Comparacion
t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_LE = r'<='
t_GE = r'>='

# Logicos: y, o, negacion
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

# Rango (1..10)
t_RANGE = r'\.\.'

# Nulos: llamada segura, valor por defecto (elvis) y asercion no nula
t_SAFE_CALL = r'\?\.'
t_ELVIS = r'\?:'
t_NOT_NULL = r'!!'
t_QUESTION = r'\?'      # tipos anulables, ej: String?

# ------------------------------------------------------------
# Fin aporte Miguel Galarza
# ------------------------------------------------------------


# ------------------------------------------------------------
# Inicio aporte William Pacalla
# Literales (numeros, Char, String) y delimitadores
# ------------------------------------------------------------

tokens += [
    'INT_LIT', 'LONG_LIT', 'DOUBLE_LIT', 'FLOAT_LIT', 'CHAR_LIT', 'STRING_LIT',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'COMA', 'DOS_PUNTOS', 'PUNTO', 'PUNTO_COMA',
    'ARROW',   # -> (when y lambdas), mejora Avance 2
]


# Los numeros van como funciones porque PLY prueba las funciones en el orden
# en que estan escritas. Primero los que tienen sufijo o decimales, si no
# "2.5f" se partiria en 2 . 5 f
def t_FLOAT_LIT(t):
    r'\d[\d_]*(\.\d[\d_]*)?[fF]'
    return t


def t_DOUBLE_LIT(t):
    r'\d[\d_]*\.\d[\d_]*'
    return t


def t_LONG_LIT(t):
    r'\d[\d_]*L'
    return t


def t_INT_LIT(t):
    r'\d[\d_]*'
    return t


# Char: un solo caracter entre comillas simples o un escape como '\n'
def t_CHAR_LIT(t):
    r"'([^'\\\n]|\\.)'"
    return t


# String entre comillas dobles. Si tiene $nombre o ${...} adentro igual queda
# como un solo token
def t_STRING_LIT(t):
    r'"([^"\\\n]|\\.)*"'
    return t


# Si las comillas no se cierran en la misma linea se reporta el error
def t_ignore_STRING_SIN_CERRAR(t):
    r'"([^"\\\n]|\\.)*'
    col = find_column(t.lexer.lexdata, t)
    t.lexer.errores.append(
        (t.lineno, col, t.value,
         f'Error léxico (línea {t.lineno}, col. {col}): el texto {t.value} no tiene comilla de cierre'))


t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMA = r','
t_DOS_PUNTOS = r':'
t_PUNTO = r'\.'
t_PUNTO_COMA = r';'
t_ARROW = r'->'


# ------------------------------------------------------------
# Fin aporte William Pacalla
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


# Crea un lexer nuevo con su lista de errores (lo usa tambien el parser.py)
def crear_lexer():
    lexer = lex.lex()
    lexer.errores = []
    return lexer


def analizar(codigo):
    lexer = crear_lexer()
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
