# semantico_jonathan.py
# ------------------------------------------------------------
# Aporte Jonathan Ramos (JonathanRamos24) - Avance 3  -  PENDIENTE
#   Regla 1 - Identificadores: una variable o funcion debe estar declarada
#             antes de usarse y dentro de su alcance.
#             val total = 5 ... println(totl)  ->  la variable "totl" no ha
#             sido declarada.
#   Regla 2 - Asignacion: una variable declarada con val o const val no puede
#             reasignarse.
#
# Para implementarlas ya existe la tabla de simbolos en estado.py:
#   estado.buscar(nombre)  -> Simbolo(nombre, tipo, mutable, ambito, linea) o None
#   estado.error_sem(linea, 'Identificadores', 'mensaje')
# (las variables, constantes y parametros ya se registran en la tabla)
# ------------------------------------------------------------
import estado
