# reglas_miguel.py
# ------------------------------------------------------------
# Inicio aporte Miguel Galarza (magselpad)
#   - ingreso de datos por teclado (readln)
#   - declaracion var (con inferencia y con tipo) y asignaciones
#   - expresiones aritmeticas con uno o mas operadores
#   - acceso a miembros, indices, llamada segura y elvis
#   - estructura de control: when
#   - estructura de datos: Map con mapOf
#   - funcion con parametros por defecto (y vararg)
# ------------------------------------------------------------
from estado import registrar, error_en, recuperar


# ---------- Numeros ----------
# operandos de las expresiones aritmeticas: 42   3.14
# (el resto de literales los agrega William en reglas_william.py)
def p_numero(p):
    '''expr : INT_LIT
            | DOUBLE_LIT'''
    registrar('literal')
    p[0] = 'expr'


# ---------- Ingreso por teclado ----------
# val texto = readln()
def p_lectura(p):
    '''expr : READLN LPAREN RPAREN'''
    registrar('lectura (readln)')
    p[0] = 'expr'


# ---------- Declaracion con var ----------
# var contador = 0       var nombre: String = "Ana"       var total: Double
def p_decl_var(p):
    '''decl_var : VAR ID ASSIGN expr
                | VAR ID DOS_PUNTOS tipo ASSIGN expr
                | VAR ID DOS_PUNTOS tipo'''
    registrar('var con tipo' if p[3] == ':' else 'var con inferencia')


# ---------- Asignaciones ----------
# x = 5      total += precio * cantidad      lista[0] = 3
# Solo se puede asignar a una variable, una propiedad o un indice
def p_asignacion(p):
    '''asignacion : expr ASSIGN expr
                  | expr PLUS_ASSIGN expr
                  | expr MINUS_ASSIGN expr
                  | expr TIMES_ASSIGN expr
                  | expr DIV_ASSIGN expr
                  | expr MOD_ASSIGN expr'''
    registrar('asignacion')
    if p[1] not in ('id', 'miembro', 'index'):
        error_en(p.lineno(2), p.lexpos(2),
                 f'el lado izquierdo de "{p[2]}" debe ser una variable, '
                 'una propiedad o un elemento de lista')


# ---------- Expresiones aritmeticas ----------
# (precio * cantidad) - descuento % 5      la precedencia esta en parser.py
def p_expr_aritmetica(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr MOD expr'''
    registrar('expresion aritmetica')
    p[0] = 'expr'


# signo: -x    +x
def p_expr_signo(p):
    '''expr : MINUS expr %prec UMINUS
            | PLUS expr %prec UMINUS'''
    registrar('expresion aritmetica')
    p[0] = 'expr'


# incremento y decremento: ++i   i++   --i   i--
def p_expr_incremento_prefijo(p):
    '''expr : INC expr %prec UMINUS
            | DEC expr %prec UMINUS'''
    registrar('incremento/decremento')
    p[0] = 'expr'


def p_expr_incremento_sufijo(p):
    '''expr : expr INC
            | expr DEC'''
    registrar('incremento/decremento')
    p[0] = 'expr'


# rango, valor por defecto (elvis), par clave-valor y casting
# 1..10      edad ?: 0      "Ana" to 20      texto as Int
def p_expr_rango(p):
    '''expr : expr RANGE expr'''
    registrar('rango')
    p[0] = 'expr'


def p_expr_elvis(p):
    '''expr : expr ELVIS expr'''
    registrar('elvis')
    p[0] = 'expr'


def p_expr_to(p):
    '''expr : expr TO expr'''
    p[0] = 'expr'


def p_expr_cast(p):
    '''expr : expr AS ID'''
    registrar('casting (as)')
    p[0] = 'expr'


# ---------- Acceso a miembros, indices y nulos ----------
# nota.size     texto.toInt()     lista[0]     a?.length     b!!
def p_expr_miembro(p):
    '''expr : expr PUNTO ID
            | expr SAFE_CALL ID'''
    registrar('acceso a miembro')
    p[0] = 'miembro'


def p_expr_llamada_miembro(p):
    '''expr : expr PUNTO ID LPAREN args_opt RPAREN
            | expr SAFE_CALL ID LPAREN args_opt RPAREN'''
    registrar('llamada a metodo')
    p[0] = 'expr'


def p_expr_indice(p):
    '''expr : expr LBRACKET expr RBRACKET'''
    registrar('indice []')
    p[0] = 'index'


def p_expr_no_nulo(p):
    '''expr : expr NOT_NULL'''
    p[0] = 'expr'


# ---------- when ----------
# when (dia) {
#     1, 7 -> println("Fin de semana")
#     in 2..5 -> println("Laboral")
#     else -> println("Otro")
# }
def p_when(p):
    '''expr : WHEN LPAREN expr RPAREN LBRACE cuerpo_when RBRACE
            | WHEN LBRACE cuerpo_when RBRACE'''
    registrar('when')
    p[0] = 'expr'


def p_cuerpo_when(p):
    '''cuerpo_when : empty
                   | seps
                   | cadena_ramas
                   | seps cadena_ramas
                   | cadena_ramas seps
                   | seps cadena_ramas seps'''


def p_cadena_ramas(p):
    '''cadena_ramas : rama_when
                    | cadena_ramas seps rama_when'''


def p_rama_when(p):
    '''rama_when : condiciones_when ARROW cuerpo_ctrl
                 | ELSE ARROW cuerpo_ctrl
                 | error'''
    recuperar(p)
    if len(p) == 4:
        registrar('rama de when')


def p_condiciones_when(p):
    '''condiciones_when : cond_when
                        | condiciones_when COMA cond_when'''


# valor, rango (in 1..5), negacion (!in) o tipo (is Int)
def p_cond_when(p):
    '''cond_when : expr
                 | IN expr
                 | NOT_IN expr
                 | IS ID
                 | NOT_IS ID'''


# ---------- Map ----------
# mapOf("Ana" to 20, "Luis" to 22)       mapOf<String, Int>()
def p_mapa(p):
    '''expr : MAPOF tipos_gen_opt LPAREN args_opt RPAREN'''
    registrar('Map (mapOf)')
    p[0] = 'expr'


# ---------- Parametros por defecto y vararg ----------
# fun saludar(nombre: String = "Mundo")       fun sumar(vararg n: Int)
def p_param_defecto(p):
    '''param : ID DOS_PUNTOS tipo ASSIGN expr'''
    registrar('parametro por defecto')


def p_param_vararg(p):
    '''param : VARARG ID DOS_PUNTOS tipo'''
    registrar('parametro vararg')
# ------------------------------------------------------------
# Fin aporte Miguel Galarza
# ------------------------------------------------------------
