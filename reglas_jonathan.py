# reglas_jonathan.py
# ------------------------------------------------------------
# Inicio aporte Jonathan Ramos (JonathanRamos24)
#   - impresion: print y println
#   - tipos de datos: Int, String?, List<Double>, Map<String, Int>, (Int) -> Int
#   - declaracion val (con tipo explicito y con inferencia)
#   - estructura de control: if / else (tambien como expresion)
#   - estructura de datos: List con listOf
#   - funciones: con tipo de retorno, de una sola expresion y return
#   - clases (constructor, propiedades y metodos), object y modificadores
# ------------------------------------------------------------
from estado import registrar, error_en, recuperar


# ---------- Impresion ----------
# print("Hola")      println("Total: $total")      println()
def p_impresion(p):
    '''expr : PRINT LPAREN expr RPAREN
            | PRINTLN LPAREN expr RPAREN
            | PRINTLN LPAREN RPAREN'''
    registrar('impresion')
    p[0] = 'expr'


# ---------- Tipos ----------
# Int      String?      List<Double>      Map<String, Int>
# Se separa tipo_base para que el ? de anulable no choque con el tipo de
# retorno de una funcion: (Int) -> Int?
def p_tipo(p):
    '''tipo : tipo_base
            | tipo_base QUESTION'''
    if len(p) == 3:
        registrar('tipo anulable')


def p_tipo_base(p):
    '''tipo_base : ID
                 | ID LT lista_tipos GT'''
    if len(p) == 5:
        registrar('tipo generico')


# tipo funcion, para guardar una lambda en una variable:
# val doble: (Int) -> Int = { x: Int -> x * 2 }
def p_tipo_funcion(p):
    '''tipo : LPAREN RPAREN ARROW tipo
            | LPAREN lista_tipos RPAREN ARROW tipo'''
    registrar('tipo funcion')


# ---------- Declaracion con val ----------
# val nombre: String = "Ana"      val total = 0.0      val edad: Int
def p_decl_val(p):
    '''decl_val : VAL ID ASSIGN expr
                | VAL ID DOS_PUNTOS tipo ASSIGN expr
                | VAL ID DOS_PUNTOS tipo'''
    registrar('val con tipo' if p[3] == ':' else 'val con inferencia')


# Conexion: val se acepta donde se acepta var y const val
def p_declaracion_val(p):
    '''declaracion_var : decl_val'''


# ---------- if / else ----------
# if (nota >= 7) { ... } else if (nota >= 5) { ... } else { ... }
# En Kotlin el if tambien es una expresion: val mayor = if (a > b) a else b
# El "else" colgante se resuelve con IFX < ELSE en la tabla de precedencia
# (parser.py): el else siempre se une al if mas cercano.
def p_if(p):
    '''expr : IF LPAREN expr RPAREN cuerpo_ctrl %prec IFX
            | IF LPAREN expr RPAREN cuerpo_ctrl ELSE cuerpo_ctrl'''
    registrar('if / else' if len(p) == 8 else 'if')
    p[0] = 'expr'


# ---------- List ----------
# listOf(8.5, 6.0, 9.25)      listOf<String>()      listOf<Int>(1, 2)
def p_lista(p):
    '''expr : LISTOF tipos_gen_opt LPAREN args_opt RPAREN'''
    registrar('List (listOf)')
    p[0] = 'expr'


# ---------- Funciones ----------
# fun main() { ... }
# fun sumar(a: Int, b: Int): Int { return a + b }
# fun doble(x: Int): Int = x * 2        (funcion de una sola expresion)
def p_funcion(p):
    '''funcion_decl : FUN ID LPAREN params_opt RPAREN retorno_opt cuerpo_funcion'''
    registrar('funcion')


def p_retorno_opt(p):
    '''retorno_opt : DOS_PUNTOS tipo
                   | empty'''
    if len(p) == 3:
        registrar('funcion con tipo de retorno')


def p_cuerpo_funcion(p):
    '''cuerpo_funcion : bloque
                      | ASSIGN expr'''
    if len(p) == 3:
        registrar('funcion de una expresion')


def p_params_opt(p):
    '''params_opt : params
                  | empty'''


def p_params(p):
    '''params : param
              | params COMA param'''


# parametro normal: nombre: String
# (los de valor por defecto y vararg estan en reglas_miguel.py)
def p_param(p):
    '''param : ID DOS_PUNTOS tipo'''


# return      return a + b
def p_return(p):
    '''sentencia_return : RETURN
                        | RETURN expr'''
    registrar('return')


# Conexion: return es una sentencia mas (tambien puede ir en un if sin llaves)
def p_sentencia_return(p):
    '''sentencia_simple : sentencia_return'''


# ---------- Clases y objetos ----------
# class Persona(val nombre: String, var edad: Int = 18) {
#     val saludo = "Hola"                       <- propiedad
#     fun cumplirAnios() { edad++ }             <- metodo
# }
# class Vacia
def p_clase(p):
    '''clase_decl : CLASS ID constructor_opt cuerpo_clase_opt'''
    registrar('clase')


# constructor primario; con val o var el parametro pasa a ser propiedad
def p_constructor_opt(p):
    '''constructor_opt : LPAREN params_clase RPAREN
                       | LPAREN RPAREN
                       | empty'''


def p_params_clase(p):
    '''params_clase : param_clase
                    | params_clase COMA param_clase'''


def p_param_clase(p):
    '''param_clase : param
                   | VAL param
                   | VAR param'''
    if len(p) == 3:
        registrar('propiedad')


def p_cuerpo_clase_opt(p):
    '''cuerpo_clase_opt : LBRACE lista_miembros RBRACE
                        | empty'''


# los miembros se separan igual que las sentencias (salto de linea o ;)
def p_lista_miembros(p):
    '''lista_miembros : empty
                      | seps
                      | cadena_miembros
                      | seps cadena_miembros
                      | cadena_miembros seps
                      | seps cadena_miembros seps'''


def p_cadena_miembros(p):
    '''cadena_miembros : miembro
                       | cadena_miembros seps miembro'''


# propiedad (val / var / const val) o metodo (fun), con o sin modificadores
def p_miembro(p):
    '''miembro : declaracion_var
               | funcion_decl
               | modificadores declaracion_var
               | modificadores funcion_decl
               | error'''
    recuperar(p)
    tipo = p.slice[-1].type
    if tipo == 'declaracion_var':
        registrar('propiedad')
    elif tipo == 'funcion_decl':
        registrar('metodo')


# object Config { const val VERSION = 1 }   (una clase con una sola instancia)
def p_objeto(p):
    '''objeto_decl : OBJECT ID LBRACE lista_miembros RBRACE'''
    registrar('object')


# ---------- Modificadores ----------
# private val clave = 1      override fun toString() = nombre      data class
# El lexer no los tiene como palabras reservadas (salen como ID), por eso aqui
# se revisa que sea uno de los que acepta Kotlin.
MODIFICADORES = {'private', 'public', 'protected', 'internal', 'open',
                 'override', 'abstract', 'data'}


def p_modificadores(p):
    '''modificadores : modificador
                     | modificadores modificador'''


def p_modificador(p):
    '''modificador : ID'''
    if p[1] not in MODIFICADORES:
        error_en(p.lineno(1), p.lexpos(1),
                 f'"{p[1]}" no es un modificador válido '
                 '(private, public, protected, internal, open, override, abstract o data)')


# Conexiones: funciones, clases y objetos van a nivel de archivo; una funcion
# tambien puede ir dentro de otra (funcion local)
def p_declaracion_top_jonathan(p):
    '''declaracion_top : funcion_decl
                       | clase_decl
                       | objeto_decl
                       | modificadores funcion_decl
                       | modificadores clase_decl
                       | modificadores objeto_decl
                       | modificadores declaracion_var'''


def p_sentencia_funcion(p):
    '''sentencia : funcion_decl'''
