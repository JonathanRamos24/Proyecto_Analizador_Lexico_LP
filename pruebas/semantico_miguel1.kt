// Miguel Galarza: semantico correcto (0 errores)
const val IVA = 0.15
val limite: Long = 5

fun total(precio: Double, cantidad: Int): Double {
    val subtotal = precio * cantidad
    val conIva = subtotal + subtotal * IVA
    return conIva
}

fun main() {
    val texto = readln()
    var edad = texto.toInt()
    edad += 1
    edad++
    var nombre = "Ana"
    nombre += edad
    val mensaje = "Edad: " + edad
    var promedio: Double = edad.toDouble() / 2
    promedio += 1
    var grande: Long = 10
    grande += edad
    val adulto = edad >= 18 && nombre != "Luis"
    val hoy = !adulto || edad > 60
    val doble = -edad * 2 + (edad % 3)
    val letras = nombre.length
    if (adulto && hoy) {
        var edad = "otra variable"
        edad = edad + 1
    }
    println(mensaje + letras + doble)
}
