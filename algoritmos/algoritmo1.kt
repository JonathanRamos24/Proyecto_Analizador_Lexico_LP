// Algoritmo de prueba - Jonathan Ramos
// Calcula el promedio de notas de un estudiante y dice si aprobo

/* Nota minima para aprobar la materia.
   /* Kotlin si permite comentarios anidados */
*/
const val NOTA_MINIMA = 7.0

fun promedio(notas: List<Double>): Double {
    var suma = 0.0
    for (n in notas) {
        suma += n
    }
    return suma / notas.size
}

fun main() {
    val nombre: String = "Jonathan"
    val notas = listOf(8.5, 6.0, 9.25)
    val prom = promedio(notas)
    var aprobado = false

    if (prom >= NOTA_MINIMA) {
        aprobado = true
        println("$nombre aprobo con $prom")
    } else {
        println("$nombre reprobo")
    }

    if (!aprobado) {
        print("Ingrese la nota del supletorio: ")
        val supletorio = readln().toDouble()
        println("Nueva nota: ${(prom + supletorio) / 2}")
    }
}
