// William Pacalla: programa correcto (no debe dar errores semanticos)
fun area(r: Double): Double {
    return r * 3.14
}

fun esPar(n: Int): Boolean {
    return n % 2 == 0
}

fun saludo(nombre: String): String {
    return "Hola " + nombre
}

fun grande(): Long {
    return 5
}

fun mostrar(texto: String) {
    println(texto)
    return
}

fun contar(limite: Int): Int {
    var total = 0
    for (i in 1..limite) {
        if (i % 2 == 0) continue
        if (total > 100) break
        total += i
    }
    var j = 0
    while (j < 10) {
        j++
        if (j == 5) break
    }
    do {
        j--
        if (j == 2) continue
    } while (j > 0)
    return total
}

fun main() {
    println(area(2.0))
    println(contar(10))
}
