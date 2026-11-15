# KotLex - Analizador Léxico y Sintáctico (subconjunto de Kotlin)

Proyecto de Lenguajes de Programación (ESPOL), hecho con Python y PLY.

## Integrantes
- Jonathan Ramos (JonathanRamos24)
- Miguel Galarza (magselpad)
- William Pacalla (williamp11)

## Estructura
- `lexer.py`: analizador léxico (Avance 1).
- `parser.py`: analizador sintáctico (Avance 2): reglas comunes, manejo de saltos de línea y errores.
- `estado.py`: funciones compartidas (errores, construcciones reconocidas).
- `reglas_miguel.py`: **listo**. `readln`, `var`, asignaciones, aritmética, números, `when`, `mapOf`, parámetros por defecto y `vararg`.
- `reglas_jonathan.py`: **listo**. impresión, tipos, `val`, if/else, `listOf`, funciones, return, clases y objetos.
- `reglas_william.py`: **listo**. literales (menos Int y Double), comparaciones, `&&` / `||`, `const val`, for/while/do-while, `setOf`, lambdas.
- `pruebas/`: 3 pruebas por integrante, `sintaxis_<nombre>1.kt` y `sintaxis_<nombre>2.kt` (correctas) y `sintaxis_<nombre>3_errores.kt` (con errores).
- `logs/`: `lexico-usuario-fecha-hora.txt` y `sintactico-usuario-fecha-hora.txt`.

Cada uno conecta sus reglas desde su archivo (`parser.py` hace `from reglas_x import *`).
Se aceptan sentencias sueltas a nivel de archivo (como un script `.kts`) porque las pruebas las usan.

## Uso
```
pip install -r requirements.txt
python parser.py archivo.kt usuarioGit
```
Genera `logs/sintactico-usuarioGit-dd-mm-aaaa-HHhMM.txt` con los errores sintácticos encontrados.

## Pendiente (Avance 3)
Análisis semántico y el resto de reglas sintácticas.
