# semantico_william.py
# Aporte William Pacalla (williamp11) - Avance 3, analizador semantico
#
#   Regla 1 - Retorno de funciones: el valor de return debe coincidir con el
#             tipo de retorno declarado en la funcion.
#             fun area(r: Double): Double { return "grande" }  ->  la funcion
#             "area" debe retornar Double, pero se retorno String.
#   Regla 2 - Estructuras de control: break y continue solo pueden usarse
#             dentro de un bucle (for, while o do-while).
#             fun main() { break }  ->  "break" solo puede usarse dentro de un
#             bucle.
#
# Las reglas sintacticas llaman a estas funciones:
#   - preparar() y finalizar(): analizar_sintaxis en parser.py
#   - registrar_salto(): p_sentencia_simple en parser.py (break y continue)
#   - verificar_return(): p_return en reglas_jonathan.py
#   - cerrar_bucle(): for / while / do-while en reglas_william.py
# Los errores se guardan con estado.error_sem().
# ------------------------------------------------------------
import estado
from estado import error_sem, tipo_de
from lexer import crear_lexer

CAT_RETORNO = 'Retorno de funciones'
CAT_CONTROL = 'Estructuras de control'

# Funciones con cuerpo entre llaves: (posicion de "{", posicion de "}", nombre,
# tipo de retorno o None). Se llena antes de analizar, igual que las funciones
# de Jonathan, porque cuando el parser reduce un return todavia no sabe en que
# funcion esta (PLY reduce de abajo hacia arriba).
funciones = []

# break / continue que todavia no estan dentro de un bucle: [posicion, linea,
# palabra]. Cuando el parser termina un bucle se quitan los que estaban dentro;
# los que quedan al final son errores.
saltos = []


# Se llama antes de analizar el archivo.
def preparar(codigo):
    funciones.clear()
    saltos.clear()
    lexer = crear_lexer()
    lexer.input(codigo)
    _buscar_funciones(list(lexer), len(codigo))


# fun nombre(params): Tipo { ... }   -> se guarda (inicio, fin, nombre, Tipo)
def _buscar_funciones(tokens, fin_codigo):
    n = len(tokens)
    for i, tok in enumerate(tokens):
        if tok.type != 'FUN' or i + 2 >= n:
            continue
        if tokens[i + 1].type != 'ID' or tokens[i + 2].type != 'LPAREN':
            continue
        nombre = tokens[i + 1].value
        j, prof = i + 2, 0                   # saltar los parametros ( ... )
        while j < n:
            if tokens[j].type == 'LPAREN':
                prof += 1
            elif tokens[j].type == 'RPAREN':
                prof -= 1
                if prof == 0:
                    break
            j += 1
        j += 1
        tipo = None
        if j < n and tokens[j].type == 'DOS_PUNTOS':     # : Tipo
            partes = []
            j += 1
            while j < n and tokens[j].type not in ('LBRACE', 'ASSIGN'):
                partes.append(str(tokens[j].value))
                j += 1
            tipo = ''.join(partes) or None
        if j >= n or tokens[j].type != 'LBRACE':
            continue                         # fun f() = expr  (sin llaves)
        inicio, prof, k = tokens[j].lexpos, 0, j
        fin = fin_codigo                     # si falta la }, llega hasta el final
        while k < n:
            if tokens[k].type == 'LBRACE':
                prof += 1
            elif tokens[k].type == 'RBRACE':
                prof -= 1
                if prof == 0:
                    fin = tokens[k].lexpos
                    break
            k += 1
        funciones.append((inicio, fin, nombre, tipo))


# funcion mas interna que contiene la posicion (o None)
def _funcion_en(pos):
    mejor = None
    for f in funciones:
        if f[0] <= pos <= f[1] and (mejor is None or f[0] > mejor[0]):
            mejor = f
    return mejor


# ---------- Regla 1: retorno de funciones ----------

# return      return expr      (valor: lo que devuelve la regla de la expresion
# o None si no hay)
def verificar_return(valor, linea, pos):
    f = _funcion_en(pos)
    if f is None:
        return                               # return suelto fuera de una funcion
    nombre, tipo = f[2], f[3]
    actual = tipo_de(valor) if valor is not None else None

    if tipo is None or tipo == 'Unit':       # fun saludar() { return "hola" }
        if actual is not None:
            error_sem(linea, CAT_RETORNO,
                      f'la función "{nombre}" no declara tipo de retorno y no '
                      f'puede retornar un {actual}.')
        return

    esperado = estado.tipo_basico(tipo)
    if esperado is None:
        return                               # List<Int>, Int?, clases: no se revisan
    if valor is None:                        # fun f(): Int { return }
        error_sem(linea, CAT_RETORNO, f'la función "{nombre}" debe retornar {esperado}.')
        return
    if actual is None or actual == esperado:
        return
    if esperado == 'Long' and actual == 'Int' and getattr(valor, 'literal', False):
        return                               # fun f(): Long { return 5 }  si se puede
    error_sem(linea, CAT_RETORNO,
              f'la función "{nombre}" debe retornar {esperado}, pero se retornó {actual}.')


# ---------- Regla 2: break y continue solo en bucles ----------

# se llama cuando el parser reconoce un break o un continue
def registrar_salto(palabra, linea, pos):
    saltos.append([pos, linea, palabra])


# se llama cuando el parser termina un for / while / do-while; "inicio" es la
# posicion de su palabra clave. Los break / continue pendientes que estan despues
# del inicio (y en la misma funcion) quedaron dentro del bucle.
def cerrar_bucle(inicio):
    funcion = _funcion_en(inicio)
    for s in list(saltos):
        if s[0] > inicio and _funcion_en(s[0]) == funcion:
            saltos.remove(s)


# se llama al terminar de analizar: lo que quedo pendiente esta fuera de un bucle
def finalizar():
    for _, linea, palabra in saltos:
        error_sem(linea, CAT_CONTROL, f'"{palabra}" solo puede usarse dentro de un bucle.')
    saltos.clear()
