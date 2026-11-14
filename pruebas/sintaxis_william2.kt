// William Pacalla: for, while, do-while, setOf y lambdas
var i = 0
var total = 0
var conjunto = setOf(1, 2, 3)
var vacio = setOf<Int>()
var nombres = setOf<String>("Ana", "Luis", "Ana")

while (i < 10) {
    i++
}
while (i > 0) i--
do {
    i++
} while (i < 5)

for (k in 1..5) {
    total += k
}
for (x in conjunto) total += x
for (n in nombres) {
    while (total > 100 || total < 0) {
        total = 0
    }
}

var doble = { x: Int -> x * 2 }
var suma = { a: Int, b: Int -> a + b }
var cuadrado = { n -> n * n }
var mayor = { a: Int, b: Int ->
    a > b
}
var resultado = doble(4)
var otro = suma(resultado, 2) + cuadrado(3)
