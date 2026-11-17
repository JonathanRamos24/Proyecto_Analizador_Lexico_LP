// Jonathan Ramos: errores semanticos de Asignacion
const val MAXIMO = 100
val nombre = "Ana"

fun main() {
    nombre = "Luis"
    MAXIMO = 200
    val edad = 20
    edad = 21
    edad += 1
    edad++
    --edad
    val nota: Double
    nota = 8.5
    nota = 9.0
    var contador = 0
    contador = 1
    for (i in 1..3) {
        i = 5
    }
}

fun cambiar(x: Int) {
    x = 10
}

class Cuenta(val numero: String, var saldo: Double) {
    fun depositar(monto: Double) {
        saldo += monto
        numero = "000"
    }
}
