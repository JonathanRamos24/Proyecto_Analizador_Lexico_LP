# KotLex - Analizador sintactico para un subconjunto de Kotlin usando PLY (yacc)
# Lenguajes de Programacion - Avance 2
# Integrantes: Jonathan Ramos, Miguel Galarza, William Pacalla
#
# Uso:   python parser.py <archivo.kt> <usuarioGit>
# Ej:    python parser.py algoritmos/algoritmo1.kt JonathanRamos24
#
# Las reglas de cada integrante estan en su propio archivo:
#   reglas_jonathan.py   reglas_miguel.py   reglas_william.py
# Aqui esta lo comun: precedencia, programa, bloques, sentencias, el manejo de
# saltos de linea, los errores sintacticos y el log.

import os
import sys
from datetime import datetime

import ply.lex as lex
import ply.yacc as yacc

import estado
from lexer import tokens as tokens_lexer, reserved, crear_lexer, find_column

# Reglas de cada integrante (PLY toma todas las funciones p_ de este modulo)
from reglas_jonathan import *   # noqa: F401,F403
from reglas_miguel import *     # noqa: F401,F403
from reglas_william import *    # noqa: F401,F403


# NL es un token que inserta FlujoTokens cuando un salto de linea separa
# sentencias (el lexer de Avance 1 ignora los saltos de linea)
tokens = list(tokens_lexer) + ['NL']

# De menor a mayor precedencia. Los operadores son de Miguel (aritmeticos,
# rango, elvis, to) y de William (logicos, comparacion, in, is).
precedence = (
    ('nonassoc', 'IFX'),            # if sin else
    ('nonassoc', 'ELSE'),
    ('right', 'ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN',
              'DIV_ASSIGN', 'MOD_ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'EQ', 'NE'),
    ('nonassoc', 'LT', 'GT', 'LE', 'GE'),
    ('nonassoc', 'IN', 'NOT_IN', 'IS', 'NOT_IS'),
    ('left', 'ELVIS'),
    ('left', 'TO'),
    ('left', 'RANGE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'AS'),
    ('right', 'UMINUS'),            # signo, !, ++ y -- prefijos
    ('left', 'PUNTO', 'SAFE_CALL', 'LBRACKET', 'NOT_NULL', 'INC', 'DEC'),
)

start = 'programa'


# ------------------------------------------------------------
# Reglas comunes
# ------------------------------------------------------------

# Un archivo es una lista de declaraciones (fun, class, object, val, var, const)
# separadas por salto de linea o ;
def p_programa(p):
    '''programa : empty
                | seps
                | cadena_decl
                | seps cadena_decl
                | cadena_decl seps
                | seps cadena_decl seps'''


def p_cadena_decl(p):
    '''cadena_decl : declaracion_top
                   | cadena_decl seps declaracion_top'''


def p_declaracion_top(p):
    '''declaracion_top : declaracion_var
                       | sentencia_simple
                       | error'''
    # TEMPORAL: se aceptan sentencias sueltas mientras no exista funcion_decl
    # (para poder probar). Quitar "sentencia_simple" cuando Jonathan la agregue
    # PENDIENTE (Jonathan): agregar aqui modificadores + funcion_decl,
    # clase_decl y objeto_decl
    estado.recuperar(p)


# val / var / const val
# PENDIENTE: Jonathan agrega "| decl_val" y William agrega "| decl_const"
def p_declaracion_var(p):
    '''declaracion_var : decl_var'''


# separadores de sentencias
def p_seps(p):
    '''seps : sep
            | seps sep'''


def p_sep(p):
    '''sep : NL
           | PUNTO_COMA'''


def p_empty(p):
    'empty :'
    pass


# bloque { ... } con sentencias separadas por salto de linea o ;
def p_bloque(p):
    '''bloque : LBRACE lista_sent RBRACE'''


def p_lista_sent(p):
    '''lista_sent : empty
                  | seps
                  | cadena_sent
                  | seps cadena_sent
                  | cadena_sent seps
                  | seps cadena_sent seps'''


def p_cadena_sent(p):
    '''cadena_sent : sentencia
                   | cadena_sent seps sentencia'''


def p_sentencia(p):
    '''sentencia : sentencia_simple
                 | declaracion_var
                 | error'''
    # PENDIENTE: Jonathan agrega "| funcion_decl" y William agrega
    # "| sentencia_for | sentencia_while | sentencia_do"
    estado.recuperar(p)


def p_sentencia_simple(p):
    '''sentencia_simple : expr %prec IFX
                        | asignacion
                        | BREAK
                        | CONTINUE'''
    # PENDIENTE (Jonathan): agregar "| sentencia_return"
    if p[1] in ('break', 'continue'):
        estado.registrar(p[1])


# cuerpo de un if / for / while / when: un bloque o una sola sentencia
def p_cuerpo_ctrl(p):
    '''cuerpo_ctrl : bloque
                   | sentencia_simple'''


# ---------- Tipos (version minima) ----------
# TEMPORAL: Jonathan reemplaza p_tipo por la completa (String?, List<Int>,
# Map<String, Int>) en reglas_jonathan.py; lista_tipos y tipos_gen_opt
# (el <Int> de listOf / mapOf / setOf) se pueden quedar aqui
def p_tipo(p):
    '''tipo : ID'''


def p_lista_tipos(p):
    '''lista_tipos : tipo
                   | lista_tipos COMA tipo'''


def p_tipos_gen_opt(p):
    '''tipos_gen_opt : LT lista_tipos GT
                     | empty'''


# ---------- Expresiones comunes ----------
def p_expr_parentesis(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = 'expr'


def p_expr_id(p):
    '''expr : ID'''
    p[0] = 'id'


# llamada a funcion: sumar(1, 2)
def p_expr_llamada(p):
    '''expr : ID LPAREN args_opt RPAREN'''
    estado.registrar('llamada a funcion')
    p[0] = 'expr'


def p_args_opt(p):
    '''args_opt : args
                | empty'''


def p_args(p):
    '''args : expr
            | args COMA expr'''


# ------------------------------------------------------------
# Flujo de tokens: agrega el token NL cuando un salto de linea separa sentencias
# ------------------------------------------------------------

# tokens despues de los cuales un salto de linea puede terminar una sentencia
FIN_SENTENCIA = {
    'ID', 'INT_LIT', 'LONG_LIT', 'DOUBLE_LIT', 'FLOAT_LIT', 'CHAR_LIT',
    'STRING_LIT', 'TRUE', 'FALSE', 'NULL', 'RPAREN', 'RBRACKET', 'RBRACE',
    'BREAK', 'CONTINUE', 'RETURN', 'INC', 'DEC', 'NOT_NULL', 'QUESTION', 'GT',
}
# si la linea siguiente empieza con uno de estos, la sentencia continua
CONTINUA_LINEA = {'PUNTO', 'SAFE_CALL', 'ELVIS', 'AND', 'OR'}
# estos nunca aparecen dentro de unos parentesis: si salen es que falto cerrar
INICIO_SENTENCIA = {'VAL', 'VAR', 'CONST', 'FUN', 'CLASS', 'OBJECT', 'FOR',
                    'WHILE', 'RETURN', 'BREAK', 'CONTINUE'}
CABECERAS = {'IF', 'WHILE', 'FOR', 'WHEN'}
ABRE = {'LPAREN': '(', 'LBRACKET': '[', 'LBRACE': '{'}
CIERRA = {'RPAREN': '(', 'RBRACKET': '[', 'RBRACE': '{'}


class FlujoTokens:
    """Envuelve al lexer. Dentro de ( ) y [ ] no hay saltos de linea que
    separen sentencias; dentro de { } y a nivel de archivo si."""

    def __init__(self, lexer):
        self.lexer = lexer
        self.reiniciar()

    def reiniciar(self):
        self.buffer = []       # tokens leidos por adelantado
        self.salida = []       # tokens listos para entregar (NL + token)
        self.previo = None
        self.pila = []         # [simbolo, linea, es_cabecera]
        self.cierra_cabecera = False
        self.while_de_do = False
        self.recuperando = False   # saltando tokens despues de un error
        self.prof = 0              # llaves abiertas mientras se salta
        self.avisos = []

    def input(self, data):
        self.reiniciar()
        self.lexer.input(data)

    def _leer(self):
        if self.buffer:
            return self.buffer.pop(0)
        return self.lexer.token()

    def _espiar(self):
        if not self.buffer:
            tok = self.lexer.token()
            if tok is not None:
                self.buffer.append(tok)
        return self.buffer[0] if self.buffer else None

    def _nl(self):
        nl = lex.LexToken()
        nl.type = 'NL'
        nl.value = '\\n'
        nl.lineno = self.previo.lineno
        nl.lexpos = self.previo.lexpos + len(str(self.previo.value))
        return nl

    def _registrar(self, tok):
        """actualiza la pila de ( [ { con el token que se entrega"""
        self.cierra_cabecera = False
        if tok.type in ABRE:
            cab = (tok.type == 'LPAREN' and self.previo is not None
                   and self.previo.type in CABECERAS
                   and not self.while_de_do)
            self.pila.append([ABRE[tok.type], tok.lineno, cab, tok.lexpos])
        elif tok.type in CIERRA:
            abre = CIERRA[tok.type]
            for i in range(len(self.pila) - 1, -1, -1):
                if self.pila[i][0] == abre:
                    self.cierra_cabecera = self.pila[i][2]
                    del self.pila[i:]
                    break
        # un "while" pegado a una } es el cierre de un do { } while (...)
        self.while_de_do = (tok.type == 'WHILE' and self.previo is not None
                            and self.previo.type == 'RBRACE')
        self.previo = tok

    def token(self):
        tok = self._siguiente()
        # modo recuperacion: se saltan tokens hasta el fin de la sentencia
        # (salto de linea o ;) o hasta la } que cierra el bloque actual,
        # sin confundirse con los { } que se abren en lo que se salta
        while self.recuperando and tok is not None:
            if tok.type == 'LBRACE':
                self.prof += 1
            elif tok.type == 'RBRACE':
                if self.prof == 0:
                    self.recuperando = False
                    break
                self.prof -= 1
            elif tok.type in ('NL', 'PUNTO_COMA') and self.prof == 0:
                self.recuperando = False
                break
            tok = self._siguiente()
        return tok

    def _siguiente(self):
        if self.salida:
            tok = self.salida.pop(0)
            self._registrar(tok)
            return tok

        tok = self._leer()
        if tok is None:
            return None

        if self.previo is not None and tok.lineno > self.previo.lineno:
            # parentesis sin cerrar: la linea nueva empieza una sentencia
            if (tok.type in INICIO_SENTENCIA and self.pila
                    and self.pila[-1][0] in '(['):
                while self.pila and self.pila[-1][0] in '([':
                    simbolo, linea, _, pos = self.pila.pop()
                    self.avisos.append((linea, pos, simbolo))
                self.cierra_cabecera = False
                tok.recuperado = True   # el error ya se informo como parentesis sin cerrar

            continua = tok.type in CONTINUA_LINEA
            if tok.type == 'ELSE':
                # "else" sigue al if de la linea anterior, salvo que sea la
                # rama "else ->" de un when
                sig = self._espiar()
                continua = not (sig is not None and sig.type == 'ARROW')
            # despues de ) de un if/while/for/when el cuerpo puede ir abajo
            if (self.previo.type in FIN_SENTENCIA and not continua
                    and not self.cierra_cabecera
                    and (not self.pila or self.pila[-1][0] == '{')):
                self.salida.append(tok)
                nl = self._nl()
                nl.recuperado = getattr(tok, 'recuperado', False)
                tok = nl
        self._registrar(tok)
        return tok


# ------------------------------------------------------------
# Errores sintacticos
# ------------------------------------------------------------

NOMBRES = {
    'NL': 'fin de línea', 'PUNTO_COMA': '";"', 'LPAREN': '"("', 'RPAREN': '")"',
    'LBRACE': '"{"', 'RBRACE': '"}"', 'LBRACKET': '"["', 'RBRACKET': '"]"',
    'COMA': '","', 'DOS_PUNTOS': '":"', 'PUNTO': '"."', 'ARROW': '"->"',
    'ASSIGN': '"="', 'LT': '"<"', 'GT': '">"', 'QUESTION': '"?"',
    'ID': 'un identificador',
}
INICIO_EXPR = {'ID', 'INT_LIT', 'LONG_LIT', 'DOUBLE_LIT', 'FLOAT_LIT',
               'CHAR_LIT', 'STRING_LIT', 'TRUE', 'FALSE', 'NULL', 'LPAREN',
               'NOT', 'IF', 'WHEN', 'PRINT', 'PRINTLN', 'READLN', 'LISTOF',
               'MAPOF', 'SETOF', 'MINUS', 'PLUS', 'INC', 'DEC', 'LBRACE'}
OPERADORES = {'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'EQ', 'NE', 'LE', 'GE',
              'LT', 'GT', 'AND', 'OR', 'RANGE', 'ELVIS', 'TO', 'AS', 'IN',
              'NOT_IN', 'NOT_IS', 'IS', 'PUNTO', 'SAFE_CALL', 'LBRACKET',
              'NOT_NULL', 'INC', 'DEC', 'ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN',
              'TIMES_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN'}
INICIO_SENT = {'VAL', 'VAR', 'FOR', 'WHILE', 'DO', 'RETURN', 'FUN'}
CONTEXTOS = {
    'IF': 'un if', 'WHILE': 'un while', 'FOR': 'un for', 'WHEN': 'un when',
    'FUN': 'una función', 'CLASS': 'una clase', 'OBJECT': 'un object',
    'LISTOF': 'listOf', 'MAPOF': 'mapOf', 'SETOF': 'setOf',
    'PRINT': 'print', 'PRINTLN': 'println', 'READLN': 'readln',
    'RETURN': 'un return',
}
PALABRAS = {tipo: palabra for palabra, tipo in reserved.items()}

flujo = None   # el FlujoTokens del analisis actual


def describir(tok):
    if tok.type == 'NL':
        return 'fin de línea'
    return f'"{tok.value}"'


def acepta(tipo):
    """El parser LALR puede hacer reducciones antes de detectar el error, asi
    que la lista de tokens de la tabla trae de mas. Aqui se simulan esas
    reducciones para saber si de verdad el token seria aceptado."""
    pila = list(parser.statestack)
    for _ in range(200):
        accion = parser.action[pila[-1]].get(tipo)
        if accion is None:
            return False
        if accion >= 0:
            return True          # desplazamiento o aceptar
        prod = parser.productions[-accion]
        if prod.len:
            del pila[-prod.len:]
        pila.append(parser.goto[pila[-1]][prod.name])
    return False


def nombre_token(t):
    if t in NOMBRES:
        return NOMBRES[t]
    if t in PALABRAS:
        return f'"{PALABRAS[t]}"'
    return t


def esperado(ok):
    """texto con lo que se esperaba en este punto"""
    if {'FUN', 'CLASS', 'OBJECT'} <= ok:
        return 'una declaración (fun, class, object, val, var o const val)'
    if len(ok & INICIO_SENT) >= 3:
        return 'una sentencia' + (' o "}"' if 'RBRACE' in ok else '')

    partes = []
    n_ops = len(ok & OPERADORES)
    if 'NL' in ok or 'PUNTO_COMA' in ok:
        partes.append('el fin de la sentencia (salto de línea o ";")')
        if n_ops >= 4:
            partes.append('un operador')
        return ' o '.join(partes)

    resto = ok
    if len(ok & INICIO_EXPR) >= 5:
        partes.append('una expresión')
        resto = resto - INICIO_EXPR
    if n_ops >= 4:
        partes.append('un operador')
        resto = resto - OPERADORES
    for t in sorted(resto):
        if t not in ('$end', 'NL', 'PUNTO_COMA', 'LT', 'GT', 'QUESTION'):
            partes.append(nombre_token(t))
    return ' o '.join(partes) if partes else 'otra construcción'


def contexto():
    """construccion mas cercana que se esta leyendo (if, for, funcion...)"""
    for sim in reversed(parser.symstack):
        if sim.type in CONTEXTOS:
            return CONTEXTOS[sim.type]
    return None


def activar_recuperacion(p):
    if flujo is None or p.type in ('NL', 'PUNTO_COMA', 'RBRACE'):
        return
    flujo.recuperando = True
    # llaves abiertas de la sentencia a medias (ej. una lambda): el parser las
    # va a descartar al recuperarse, por eso sus } no deben cerrar el bloque
    prof = 1 if p.type == 'LBRACE' else 0
    for i in range(len(parser.statestack) - 1, 0, -1):
        if parser.action[parser.statestack[i]].get('error') is not None:
            break
        if parser.symstack[i].type == 'LBRACE':
            prof += 1
    flujo.prof = prof


ultimo_error = None   # ultimo token que dio error (para no repetir el mismo)


def p_error(p):
    global ultimo_error
    # si el mismo token vuelve a dar error, se descarta y se sigue con el
    # siguiente (si no, el parser se queda dando vueltas en el mismo token)
    if p is not None and p is ultimo_error:
        parser.errok()
        return flujo.token()
    ultimo_error = p
    if p is None:
        # se acabo el archivo y la gramatica esperaba mas
        if flujo is not None and flujo.pila:
            simbolo, linea, _, pos = flujo.pila[-1]
            cierre = {'(': ')', '[': ']', '{': '}'}[simbolo]
            msg = (f'Error sintáctico (línea {linea}, col. {estado.columna(pos)}): '
                   f'fin de archivo inesperado, falta cerrar "{simbolo}" con "{cierre}"')
        else:
            msg = 'Error sintáctico: fin de archivo inesperado, la última construcción está incompleta'
        estado.errores.append((10 ** 9, 0, msg))
        return

    if getattr(p, 'recuperado', False):
        activar_recuperacion(p)
        return   # ya se informo que falto cerrar un parentesis
    col = find_column(estado.codigo, p)
    ok = {t for t in parser.action[parser.statestack[-1]] if acepta(t)}
    ctx = contexto()
    msg = f'se encontró {describir(p)} pero se esperaba {esperado(ok)}'
    if ctx:
        msg += f' (dentro de {ctx})'
    if 'RPAREN' in ok and p.type in ('LBRACE', 'NL') and ctx in ('un if', 'un while', 'un for', 'un when'):
        msg = (f'se encontró {describir(p)} pero se esperaba ")" para cerrar '
               f'la condición de {ctx}')
    estado.errores.append((p.lineno, col,
                           f'Error sintáctico (línea {p.lineno}, col. {col}): {msg}'))
    activar_recuperacion(p)


# ------------------------------------------------------------
# Construccion del parser y analisis
# ------------------------------------------------------------

# mientras faltan reglas de otros integrantes PLY avisa de tokens sin usar;
# esos avisos se ocultan, los demas (conflictos, errores) se siguen mostrando
class AvisosPLY(yacc.PlyLogger):
    def warning(self, msg, *args, **kwargs):
        if 'not used' in msg or 'unused' in msg or 'unreachable' in msg:
            return
        super().warning(msg, *args, **kwargs)


parser = yacc.yacc(debug=False, write_tables=False,
                   errorlog=AvisosPLY(sys.stderr))


def analizar_sintaxis(codigo):
    """Devuelve (errores_lexicos, errores_sintacticos, construcciones)"""
    global flujo, ultimo_error
    ultimo_error = None
    estado.reiniciar(codigo)
    lexer = crear_lexer()
    flujo = FlujoTokens(lexer)
    parser.parse(codigo, lexer=flujo)

    errores_sint = list(estado.errores)
    # parentesis que quedaron sin cerrar y que el flujo cerro solo
    lineas_con_error = {e[0] for e in errores_sint}
    for linea, pos, simbolo in flujo.avisos:
        if linea in lineas_con_error:
            continue   # ya hay un error sintactico en esa linea
        cierre = {'(': ')', '[': ']'}[simbolo]
        col = estado.columna(pos)
        errores_sint.append((linea, col,
                             f'Error sintáctico (línea {linea}, col. {col}): '
                             f'falta cerrar "{simbolo}" con "{cierre}"'))
    errores_sint.sort(key=lambda e: (e[0], e[1]))
    return lexer.errores, errores_sint, dict(estado.construcciones)


def guardar_log(archivo, usuario, err_lex, err_sint, construcciones):
    os.makedirs('logs', exist_ok=True)
    ahora = datetime.now()
    nombre = f"logs/sintactico-{usuario}-{ahora.strftime('%d-%m-%Y-%Hh%M')}.txt"

    with open(nombre, 'w', encoding='utf-8') as f:
        f.write('KotLex - Analizador sintactico\n')
        f.write(f'Archivo: {archivo}\n')
        f.write(f'Usuario: {usuario}\n')
        f.write(f"Fecha:   {ahora.strftime('%d/%m/%Y %H:%M:%S')}\n\n")

        f.write(f'Errores lexicos ({len(err_lex)}):\n')
        if not err_lex:
            f.write('Ninguno\n')
        for e in err_lex:
            f.write(e[3] + '\n')

        f.write(f'\nErrores sintacticos ({len(err_sint)}):\n')
        if not err_sint:
            f.write('Ninguno\n')
        for e in err_sint:
            f.write(e[2] + '\n')

        f.write('\nConstrucciones reconocidas:\n')
        for nombre_c in sorted(construcciones):
            f.write(f'{nombre_c:<30}{construcciones[nombre_c]}\n')

        if err_sint or err_lex:
            f.write(f'\nResultado: {len(err_lex)} errores lexicos y {len(err_sint)} errores sintacticos\n')
        else:
            f.write('\nResultado: analisis sintactico correcto\n')
    return nombre


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: python parser.py <archivo.kt> <usuarioGit>')
        sys.exit(1)

    archivo, usuario = sys.argv[1], sys.argv[2]
    with open(archivo, encoding='utf-8') as f:
        codigo = f.read()

    err_lex, err_sint, construcciones = analizar_sintaxis(codigo)
    for e in err_lex:
        print(e[3])
    for e in err_sint:
        print(e[2])

    log = guardar_log(archivo, usuario, err_lex, err_sint, construcciones)
    if not err_lex and not err_sint:
        print('Analisis sintactico correcto')
    print(f'{len(err_lex)} errores lexicos, {len(err_sint)} errores sintacticos. Log guardado en {log}')
