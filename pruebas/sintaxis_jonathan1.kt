// Jonathan Ramos: impresion, val con tipo, tipos, listOf e if / else
val nombre: String = "Jonathan"
val edad = 21
val apodo: String? = null
val notas: List<Double> = listOf(8.5, 6.0, 9.25)
val vacia = listOf<String>()
val edades: Map<String, Int> = mapOf("Ana" to 20)
val doble: (Int) -> Int = { x: Int -> x * 2 }

print("Hola ")
println(nombre)
println()

if (edad >= 18) {
    println("Mayor de edad")
} else {
    println("Menor de edad")
}

if (notas[0] >= 7.0 && edad > 18) println("Aprobado") else println("Reprobado")

if (edad < 13) {
    println("Nino")
} else if (edad < 18) {
    println("Adolescente")
} else {
    println("Adulto")
}

val mayor = if (edad > 30) edad else 30
println("Mayor: $mayor, doble: ${doble(mayor)}")
