// William Pacalla: errores semanticos de Estructuras de control
fun main() {
    break
    val n = 3
    if (n > 2) {
        continue
    }
    for (i in 1..n) {
        if (i == 2) break
    }
    continue
    while (n > 0) {
        continue
    }
}

fun otra(): Int {
    val x = 1
    if (x > 0) break
    return x
}
