// Jonathan Ramos: funciones con retorno, return, clases, propiedades, metodos y object
fun sumar(a: Int, b: Int): Int {
    return a + b
}

fun promedio(notas: List<Double>): Double {
    if (notas.size == 0) return 0.0
    var suma = 0.0
    for (n in notas) {
        suma += n
    }
    return suma / notas.size
}

fun doble(x: Int): Int = x * 2

fun saludar(nombre: String = "Mundo") {
    println("Hola $nombre")
    return
}

class Estudiante(val nombre: String, var nota: Double = 0.0) {
    val materia = "Lenguajes de Programacion"
    private var intentos = 0

    fun aprobo(): Boolean {
        return nota >= 7.0
    }

    fun subirNota(puntos: Double) {
        nota += puntos
        intentos++
    }

    override fun toString(): String = "$nombre: $nota"
}

data class Punto(val x: Int, val y: Int)

class Vacia

object Configuracion {
    const val NOTA_MINIMA = 7.0
    val version = "1.0"
}

fun main() {
    val estudiante = Estudiante("Jonathan", 6.5)
    estudiante.subirNota(1.0)
    println(estudiante.aprobo())
    println(sumar(2, 3) + doble(4))
    println(Configuracion.NOTA_MINIMA)
    val p = Punto(1, 2)
    fun local(): Int = p.x + p.y
    println(local())
}
