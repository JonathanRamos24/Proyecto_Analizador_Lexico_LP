// Algoritmo de prueba - Miguel Galarza
// Calculadora de facturas con descuentos, usa var, when, Map y parametros por defecto
/* Calculadora de facturas con descuentos por categoria */

fun saludar(nombre: String = "Mundo", veces: Int = 1) {
    var i = 0
    while (i < veces) {
        println("Hola " + nombre)
        i++
    }
}

fun descuento(categoria: String): Int {
    when (categoria) {
        "A", "B" -> return 10
        "C" -> return 5
        else -> return 0
    }
}

fun main() {
    var precio = 25.5
    var cantidad = 4
    var contador = 0
    val edades = mapOf("Ana" to 20, "Luis" to 22, "Eva" to 31)
    val vacio: Map<String, Int> = mapOf()

    var total = (precio * cantidad) - descuento("A") % 5
    total = total + 10 / 2 - 3 * 4
    total += 1.5
    total -= 0.5
    total *= 2
    total /= 4
    cantidad %= 3
    contador++
    contador--
    val negativo = -total

    val dia = 3
    when (dia) {
        1, 7 -> println("Fin de semana")
        in 2..5 -> println("Laboral")
        !in 1..7 -> println("Invalido")
        else -> println("Sabado")
    }

    val clave = "Ana"
    val edad = edades[clave] ?: 0
    val texto: Any = edad
    if (texto is Int && texto !is String) {
        println("Es entero")
    }
    val maybe = edades.get("Luis")?.toString()
    val seguro = maybe!!.length
    val esIgual = (seguro == 2) || (seguro != 3)
    val cmp = precio > 10.0 && precio >= 5.0 && cantidad < 9 && cantidad <= 8
    saludar()
    saludar("Kotlin", 2)
    val casteo = texto as Int
    print(casteo)
    println(esIgual)
    println(cmp)
    println(negativo)
    println(vacio)
}
