// William Pacalla: literales, const val y condiciones
const val MAX_FALTAS = 4
const val PI: Double = 3.14159
const val SALUDO = "Hola"
const val LIMITE: Long = 9000000000L

var largo = 9000000000L
var flotante = 2.5f
var letra = 'W'
var salto = '\n'
var texto = "Edad: $largo \"ok\""
var activo = true
var inactivo = false
var nada = null
var entero = 1_000
var decimal = 0.75

var a = 5
var b = 10
var r1 = a == b
var r2 = a != b
var r3 = a < b
var r4 = a > b
var r5 = a <= b
var r6 = a >= b
var r7 = a > 1 && b < 20
var r8 = a == 1 || b == 2 && !activo
var r9 = !(a > b) || (a <= 3 && b >= 4)
var r10 = a + 1 > b * 2 && !inactivo
