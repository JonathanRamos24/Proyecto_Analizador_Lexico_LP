# reglas_william.py
# ------------------------------------------------------------
# Aporte William Pacalla (williamp11)
#   - literales: Long, Float, Char, String, true, false, null
#     (INT_LIT y DOUBLE_LIT ya estan en reglas_miguel.py: aqui no se repiten)
#   - condiciones: comparaciones, conectores logicos y negacion
#   - declaracion const val
#   - estructuras de control: for, while y do-while
#   - estructura de datos: Set con setOf (con o sin tipo generico)
#   - funcion lambda: { x: Int -> x * 2 }
#

# ------------------------------------------------------------
from estado import registrar


# ---------- Literales ----------
# 9000000000L    2.5f    'W'    '\n'    "Hola $nombre"
# (la interpolacion de la cadena la resuelve el lexer: es un solo STRING_LIT)
def p_literal_william(p):
    '''expr : LONG_LIT
            | FLOAT_LIT
            | CHAR_LIT
            | STRING_LIT'''
    registrar('literal')
    p[0] = 'expr'


# true    false
def p_literal_booleano(p):
    '''expr : TRUE
            | FALSE'''
    registrar('literal booleano')
    p[0] = 'expr'


# null
def p_literal_nulo(p):
    '''expr : NULL'''
    registrar('literal null')
    p[0] = 'expr'


# ---------- Condiciones ----------
# Comparaciones: a == b   a != b   a < b   a > b   a <= b   a >= b
# La precedencia y la asociatividad estan en la tabla "precedence" de parser.py
def p_comparacion(p):
    '''expr : expr EQ expr
            | expr NE expr
            | expr LT expr
            | expr GT expr
            | expr LE expr
            | expr GE expr'''
    registrar('comparacion')
    p[0] = 'expr'


# Conectores logicos: a > 1 && b < 5      x == 0 || y == 0
def p_conector_logico(p):
    '''expr : expr AND expr
            | expr OR expr'''
    registrar('conector logico')
    p[0] = 'expr'


# pertenencia y tipo: x in lista    x !in 1..5    y is String    y !is Int
def p_pertenencia(p):
    '''expr : expr IN expr
            | expr NOT_IN expr'''
    registrar('pertenencia (in)')
    p[0] = 'expr'


def p_es_tipo(p):
    '''expr : expr IS ID
            | expr NOT_IS ID'''
    registrar('verificacion de tipo (is)')
    p[0] = 'expr'


# Negacion: !activo      !(a > b)
def p_negacion(p):
    '''expr : NOT expr %prec UMINUS'''
    registrar('negacion (!)')
    p[0] = 'expr'


# ---------- const val ----------
# const val MAX = 4        const val PI: Double = 3.14159
def p_decl_const(p):
    '''decl_const : CONST VAL ID ASSIGN expr
                  | CONST VAL ID DOS_PUNTOS tipo ASSIGN expr'''
    registrar('const val con tipo' if p[4] == ':' else 'const val con inferencia')


# Conexion: const val se acepta donde se acepta val / var
def p_declaracion_const(p):
    '''declaracion_var : decl_const'''


# ---------- for ----------
# for (i in 1..10) { ... }      for (x in conjunto) total += x
def p_sentencia_for(p):
    '''sentencia_for : FOR LPAREN ID IN expr RPAREN cuerpo_ctrl'''
    registrar('estructura for')


# ---------- while ----------
# while (i < 10) { i++ }
def p_sentencia_while(p):
    '''sentencia_while : WHILE LPAREN expr RPAREN cuerpo_ctrl'''
    registrar('estructura while')


# ---------- do-while ----------
# do { i++ } while (i < 10)
def p_sentencia_do(p):
    '''sentencia_do : DO cuerpo_ctrl WHILE LPAREN expr RPAREN'''
    registrar('estructura do-while')


# Conexion: for / while / do-while como sentencia dentro de un bloque
def p_sentencia_control(p):
    '''sentencia : sentencia_for
                 | sentencia_while
                 | sentencia_do'''


# TEMPORAL: igual que "sentencia_simple" en p_declaracion_top (parser.py), se
# aceptan a nivel de archivo mientras no exista funcion_decl. Cuando Jonathan
# agregue las funciones, esta regla se puede quitar (en Kotlin un for/while va
# dentro de una funcion).
def p_declaracion_top_control(p):
    '''declaracion_top : sentencia_for
                       | sentencia_while
                       | sentencia_do'''


# ---------- Set ----------
# setOf(1, 2, 3)      setOf<Int>()      setOf<String>("a", "b")
# tipos_gen_opt (el <Int>) esta en parser.py y lo comparte con listOf y mapOf
def p_conjunto(p):
    '''expr : SETOF tipos_gen_opt LPAREN args_opt RPAREN'''
    registrar('Set (setOf)')
    p[0] = 'expr'


# ---------- Lambda ----------
# { x: Int -> x * 2 }      { a: Int, b: Int -> a + b }      { n -> n * n }
# Los parametros y la flecha son obligatorios: sin ellos { ... } no se puede
# distinguir de un bloque.
def p_lambda(p):
    '''expr : LBRACE params_lambda ARROW lista_sent RBRACE'''
    registrar('lambda')
    p[0] = 'expr'


def p_params_lambda(p):
    '''params_lambda : param_lambda
                     | params_lambda COMA param_lambda'''


def p_param_lambda(p):
    '''param_lambda : ID
                    | ID DOS_PUNTOS tipo'''
    registrar('parametro de lambda')
