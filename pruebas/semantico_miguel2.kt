// Miguel Galarza: errores semanticos de Operaciones permitidas
fun main() {
    val a = "hola" - 3
    val precio = 10.5
    val etiqueta = "Total"
    var total = etiqueta * precio
    val activo = true
    val suma = activo + 1
    val edad = 20
    val mal = edad && activo
    val peor = activo || "si"
    var texto = "abc"
    texto++
    val neg = -etiqueta
    val ok = (edad + 3) * 2 - 1
}
