// Miguel Galarza: when, mapOf, elvis, rango, miembros e indices
var edades = mapOf(a to 20, b to 22)
var vacio = mapOf<String, Int>()
var dia = readln()
var mensaje = 0
when (dia) {
    1, 7 -> mensaje = 1
    in 2..5 -> mensaje = 2
    !in 8..9 -> mensaje = 3
    is Int -> mensaje = 4
    else -> {
        mensaje = 0
        mensaje += 1
    }
}
when {
    activo -> mensaje = 5
    else -> mensaje = 6
}
var nota = lista[0]
lista[1] = nota ?: 0
var largo = texto.length
var n = texto.toInt()
var seguro = persona?.nombre
var fuerte = valor!!
var conv = texto as Int
