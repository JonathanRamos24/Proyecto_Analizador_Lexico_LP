// Miguel Galarza: errores semanticos de Conversion
val precio: Double = 5
const val MAX: Int = 3.5

fun main() {
    val edad: Int = readln()
    var nota: Int = 10
    nota = 8.5
    var total: Double = 0.0
    total = nota
    nota += 2.5
    var mensaje: String = 100
    val ok1: Double = nota.toDouble()
    val ok2: Long = 7
    var activo: Boolean = nota
    total += nota
}
