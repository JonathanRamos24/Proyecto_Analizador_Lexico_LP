// Jonathan Ramos: semantico correcto (0 errores)
const val NOTA_MINIMA = 7.0

fun main() {
    val nombre = "Jonathan"
    var nota = 6.5
    nota += 1.0
    val edad: Int
    edad = 21
    var intentos = 0
    intentos++
    val doble = { x: Int -> x * 2 }
    for (i in 1..3) {
        val parcial = i * 2
        println(parcial)
    }
    for (n in listOf(1, 2, 3)) println(n)
    if (nota >= NOTA_MINIMA) {
        val mensaje = "Aprobado"
        println(mensaje)
    }
    println(promedio(nota, 8.0))
    val e = Estudiante(nombre, nota)
    e.subirNota(0.5)
    println(doble(edad) + intentos)
}

fun promedio(a: Double, b: Double): Double = (a + b) / 2

class Estudiante(val nombre: String, var nota: Double) {
    fun subirNota(puntos: Double) {
        nota += puntos
    }
}
