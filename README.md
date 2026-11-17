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
- `semantico.py`: analizador semántico (Avance 3). Uso: `python semantico.py archivo.kt usuarioGit`.
- `semantico_miguel.py`: **listo**. Reglas semánticas de Miguel: Operaciones permitidas y Conversión.
- `semantico_jonathan.py`: **pendiente**. Identificadores y Asignación (val no reasignable).
- `semantico_william.py`: **pendiente**. Retorno de funciones y break/continue solo en bucles.
- `pruebas/`: 3 pruebas por integrante, `sintaxis_<nombre>1.kt` y `sintaxis_<nombre>2.kt` (correctas) y `sintaxis_<nombre>3_errores.kt` (con errores).
- `pruebas/semantico_miguel1.kt` (correcta), `semantico_miguel2.kt` (Operaciones permitidas) y `semantico_miguel3.kt` (Conversión).
- `logs/`: `lexico-...`, `sintactico-...` y `semantico-usuario-ddmmaaaa-HHhMM.txt`.

La tabla de símbolos (nombre, tipo, mutabilidad, ámbito) está en `estado.py`; los ámbitos siguen a las llaves `{ }`.

Cada uno conecta sus reglas desde su archivo (`parser.py` hace `from reglas_x import *`).
Se aceptan sentencias sueltas a nivel de archivo (como un script `.kts`) porque las pruebas las usan.

## Uso
```
pip install -r requirements.txt
python parser.py archivo.kt usuarioGit
```
Genera `logs/sintactico-usuarioGit-dd-mm-aaaa-HHhMM.txt` con los errores sintácticos encontrados.

## Semántico
```
python semantico.py archivo.kt usuarioGit
```
Genera `logs/semantico-usuarioGit-ddmmaaaa-HHhMM.txt` con los errores semánticos y la tabla de símbolos.
