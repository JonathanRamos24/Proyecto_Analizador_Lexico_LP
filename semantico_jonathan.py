# semantico_jonathan.py
# ------------------------------------------------------------
# Inicio aporte Jonathan Ramos (JonathanRamos24) - Avance 3, analizador semantico
#
#   Regla 1 - Identificadores: una variable o funcion debe estar declarada
#             antes de usarse y dentro de su alcance.
#             val total = 5 ... println(totl)  ->  la variable "totl" no ha
#             sido declarada.
#   Regla 2 - Asignacion: una variable declarada con val o const val no puede
#             reasignarse (tampoco los parametros de una funcion, que en
#             Kotlin son val). Un val declarado sin valor (val x: Int) si
#             puede recibir su primer valor despues.
#
# Las reglas sintacticas llaman a estas funciones (p_expr_id y p_expr_llamada
# en parser.py, p_asignacion y ++ / -- en reglas_miguel.py).
# ------------------------------------------------------------
import estado
from estado import error_sem
from lexer import crear_lexer

CAT_IDENTIFICADORES = 'Identificadores'
CAT_ASIGNACION = 'Asignación'

# funciones de la libreria estandar que el lexer saca como ID
# (println, listOf, readln... ya son tokens aparte)
FUNCIONES_KOTLIN = {'maxOf', 'minOf', 'arrayOf', 'intArrayOf', 'mutableListOf',
                    'mutableMapOf', 'mutableSetOf', 'emptyList', 'emptyMap',
                    'emptySet', 'repeat', 'require', 'check', 'error', 'TODO'}

funciones = set()        # funciones, clases y objects declarados en el archivo
val_sin_valor = []       # val x: Int  (todavia se les puede dar un valor)


# Se llama antes de analizar. En Kotlin una funcion o clase se puede usar
# antes de la linea donde se declara (main puede estar al inicio), por eso
# primero se buscan todos los "fun nombre", "class Nombre" y "object Nombre".
def preparar(codigo):
    funciones.clear()
    val_sin_valor.clear()
    lexer = crear_lexer()
    lexer.input(codigo)
    anterior = None
    for tok in lexer:
        if tok.type == 'ID' and anterior in ('FUN', 'CLASS', 'OBJECT'):
            funciones.add(tok.value)
        anterior = tok.type


# ---------- Regla 1: identificadores ----------

# parametros de un for o de una funcion de una sola linea que todavia no
# entran a un ambito:  for (x in lista) total += x    fun doble(n: Int) = n * 2
def _es_parametro_pendiente(nombre):
    return any(p[0] == nombre for p in estado.params_pendientes)


# x  (una variable usada en una expresion)
def verificar_identificador(nombre, linea):
    if estado.buscar(nombre) or _es_parametro_pendiente(nombre):
        return
    if nombre in funciones:
        return                    # Configuracion.VERSION  (un object o clase)
    # si existe pero en un bloque que ya se cerro, esta fuera de su alcance
    otra = [s for s in estado.simbolos if s.nombre == nombre]
    if otra:
        error_sem(linea, CAT_IDENTIFICADORES,
                  f'la variable "{nombre}" no existe en este alcance '
                  f'(se declaró en la línea {otra[-1].linea}, dentro de otro bloque).')
    else:
        error_sem(linea, CAT_IDENTIFICADORES,
                  f'la variable "{nombre}" no ha sido declarada.')


# sumar(1, 2)   Persona("Ana")
def verificar_funcion(nombre, linea):
    if nombre in funciones or nombre in FUNCIONES_KOTLIN:
        return
    if estado.buscar(nombre) or _es_parametro_pendiente(nombre):
        return                    # val doble = { x: Int -> x * 2 } ... doble(3)
    error_sem(linea, CAT_IDENTIFICADORES,
              f'la función "{nombre}" no ha sido declarada.')


# ---------- Regla 2: asignacion ----------

# x = 5   x += 1   x++   (destino es lo que devuelve p_expr_id)
def verificar_reasignacion(destino, linea):
    nombre = getattr(destino, 'nombre', None)
    if destino != 'id' or nombre is None:
        return                    # lista[0] = 1   persona.edad = 2  no se revisan
    s = estado.buscar(nombre)
    if s is None or s.mutable:
        return                    # si no existe ya lo marca la regla 1
    if s in val_sin_valor:
        val_sin_valor.remove(s)   # primer valor de un val x: Int
        return
    error_sem(linea, CAT_ASIGNACION,
              f'"{nombre}" es un val (línea {s.linea}) y no se puede reasignar. '
              'Use var si necesita cambiar su valor.')


# val x: Int   (sin valor): se guarda para permitir la primera asignacion
def val_declarado_sin_valor(nombre):
    s = estado.buscar(nombre)
    if s is not None:
        val_sin_valor.append(s)

# ------------------------------------------------------------
# Fin aporte Jonathan Ramos
# ------------------------------------------------------------
