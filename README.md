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
- `reglas_jonathan.py`: **pendiente**. impresión, tipos, `val`, if/else, `listOf`, funciones, return, clases y objetos.
- `reglas_william.py`: **pendiente**. literales (menos Int y Double), comparaciones, `&&` / `||`, `const val`, for/while/do-while, `setOf`, lambdas.
- `pruebas/`: `sintaxis_miguel1.kt`, `sintaxis_miguel2.kt` (correctas) y `sintaxis_miguel3_errores.kt` (con errores).
- `logs/`: `lexico-usuario-fecha-hora.txt` y `sintactico-usuario-fecha-hora.txt`.

Los lugares de `parser.py` que cada uno debe conectar están marcados con `PENDIENTE`.
`tipo` y `declaracion_top : sentencia_simple` son temporales (ver comentarios).

## Uso
```
pip install -r requirements.txt
python parser.py archivo.kt usuarioGit
```
Genera `logs/sintactico-usuarioGit-dd-mm-aaaa-HHhMM.txt` con los errores sintácticos encontrados.

## Pendiente (Avance 3)
Análisis semántico y el resto de reglas sintácticas.
