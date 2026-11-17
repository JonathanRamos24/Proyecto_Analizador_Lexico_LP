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
from estado import registrar, Valor
import estado
import semantico_miguel as sem
import semantico_william as sem_william


# ---------- Literales ----------
# 9000000000L    2.5f    'W'    '\n'    "Hola $nombre"
# (la interpolacion de la cadena la resuelve el lexer: es un solo STRING_LIT)
def p_literal_william(p):
    '''expr : LONG_LIT
            | FLOAT_LIT
            | CHAR_LIT
            | STRING_LIT'''
    registrar('literal')
    # semantico: tipo de cada literal
    tipos = {'LONG_LIT': 'Long', 'FLOAT_LIT': 'Float', 'CHAR_LIT': 'Char',
             'STRING_LIT': 'String'}
    p[0] = Valor('expr', tipos[p.slice[1].type])


# true    false
def p_literal_booleano(p):
    '''expr : TRUE
            | FALSE'''
    registrar('literal booleano')
    p[0] = Valor('expr', 'Boolean')


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
    p[0] = Valor('expr', 'Boolean')


# Conectores logicos: a > 1 && b < 5      x == 0 || y == 0
def p_conector_logico(p):
    '''expr : expr AND expr
            | expr OR expr'''
    registrar('conector logico')
    sem.verificar_logico(p[2], p[1], p[3], p.lineno(2))   # semantico (Miguel)
    p[0] = Valor('expr', 'Boolean')


# pertenencia y tipo: x in lista    x !in 1..5    y is String    y !is Int
def p_pertenencia(p):
    '''expr : expr IN expr
            | expr NOT_IN expr'''
    registrar('pertenencia (in)')
    p[0] = Valor('expr', 'Boolean')


def p_es_tipo(p):
    '''expr : expr IS ID
            | expr NOT_IS ID'''
    registrar('verificacion de tipo (is)')
    p[0] = Valor('expr', 'Boolean')


# Negacion: !activo      !(a > b)
def p_negacion(p):
    '''expr : NOT expr %prec UMINUS'''
    registrar('negacion (!)')
    p[0] = Valor('expr', 'Boolean')


# ---------- const val ----------
# const val MAX = 4        const val PI: Double = 3.14159
def p_decl_const(p):
    '''decl_const : CONST VAL ID ASSIGN expr
                  | CONST VAL ID DOS_PUNTOS tipo ASSIGN expr'''
    registrar('const val con tipo' if p[4] == ':' else 'const val con inferencia')
    # semantico: tabla de simbolos y conversion (regla Conversion de Miguel)
    if len(p) == 6:                       # const val X = expr
        sem.declarar_variable(p[3], None, p[5], False, p.lineno(1))
    else:                                 # const val X: Tipo = expr
        sem.declarar_variable(p[3], p[5], p[7], False, p.lineno(1))


# Conexion: const val se acepta donde se acepta val / var
def p_declaracion_const(p):
    '''declaracion_var : decl_const'''


# ---------- for ----------
# for (i in 1..10) { ... }      for (x in conjunto) total += x
def p_sentencia_for(p):
    '''sentencia_for : FOR LPAREN iterador IN expr RPAREN cuerpo_ctrl'''
    registrar('estructura for')
    sem_william.cerrar_bucle(p.lexpos(1))   # semantico: break / continue dentro del bucle


# semantico (Jonathan): la variable del for entra al ambito del cuerpo y es
# un val (no se puede reasignar dentro del for)
def p_iterador(p):
    '''iterador : ID'''
    estado.param_pendiente(p[1], None)


# ---------- while ----------
# while (i < 10) { i++ }
def p_sentencia_while(p):
    '''sentencia_while : WHILE LPAREN expr RPAREN cuerpo_ctrl'''
    registrar('estructura while')
    sem_william.cerrar_bucle(p.lexpos(1))   # semantico: break / continue dentro del bucle


# ---------- do-while ----------
# do { i++ } while (i < 10)
def p_sentencia_do(p):
    '''sentencia_do : DO cuerpo_ctrl WHILE LPAREN expr RPAREN'''
    registrar('estructura do-while')
    sem_william.cerrar_bucle(p.lexpos(1))   # semantico: break / continue dentro del bucle


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
    # semantico (Jonathan): el { de la lambda ya abrio su ambito
    estado.declarar(p[1], p[3] if len(p) == 4 else None, False, p.lineno(1))
