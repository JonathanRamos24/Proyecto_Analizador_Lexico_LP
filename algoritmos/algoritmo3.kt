// Algoritmo de prueba - William Pacalla
// Asistencia de un curso: cuenta estudiantes unicos y quienes aprueban por faltas

const val MAX_FALTAS = 4

fun main() {
    val asistentes = setOf("Ana", "Luis", "Maria", "Ana")
    val faltas = listOf(1, 3, 5, 0)
    val totalClases = 16
    val porcentajeMinimo = 0.75
    val peso = 2.5f
    val creditos = 1_000
    val poblacion = 9000000000L
    val inicial: Char = 'W'
    val salto = '\n'
    val doble = { x: Int -> x * 2 }

    var clasesDadas = 0
    for (i in 1..totalClases) {
        if (i % 4 == 0) continue
        clasesDadas++
    }

    var aprobados = 0
    for (f in faltas) {
        if (f > 10) break
        val asistencia = (totalClases - f).toDouble() / totalClases
        val aprueba = asistencia >= porcentajeMinimo && f <= MAX_FALTAS
        if (aprueba) aprobados++
    }

    println("Registro \"Lenguajes\" de $inicial$salto");
    println("Estudiantes unicos: ${asistentes.size}")
    println("Primera falta: ${faltas[0]}, clases dadas: $clasesDadas")
    println("Aprobados: $aprobados, el doble: ${doble(aprobados)}")
    println("Datos: $peso $creditos $poblacion")
}
