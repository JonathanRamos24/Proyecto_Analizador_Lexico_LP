# KotLex - Analizador semantico (Avance 3)
# Lenguajes de Programacion
#
# Uso:   python semantico.py <archivo.kt> <usuarioGit>
# Ej:    python semantico.py pruebas/semantico_miguel2.kt magselpad
#
# Las reglas semanticas de cada integrante estan en su archivo:
#   semantico_jonathan.py   semantico_miguel.py   semantico_william.py
# Este programa analiza el archivo (lexico + sintactico + semantico) y guarda
# un log con los errores semanticos y la tabla de simbolos.

import os
import sys
from datetime import datetime

import estado
from parser import analizar_sintaxis


def guardar_log(archivo, usuario, err_lex, err_sint):
    os.makedirs('logs', exist_ok=True)
    ahora = datetime.now()
    nombre = f"logs/semantico-{usuario}-{ahora.strftime('%d%m%Y-%Hh%M')}.txt"
    errores = sorted(estado.errores_sem, key=lambda e: e[0])

    with open(nombre, 'w', encoding='utf-8') as f:
        f.write('KotLex - Analizador semantico\n')
        f.write(f'Archivo: {archivo}\n')
        f.write(f'Usuario: {usuario}\n')
        f.write(f"Fecha:   {ahora.strftime('%d/%m/%Y %H:%M:%S')}\n\n")

        f.write(f'Errores semanticos ({len(errores)}):\n')
        if not errores:
            f.write('Ninguno\n')
        for linea, categoria, mensaje in errores:
            f.write(f'Error semántico [{categoria}] (línea {linea}): {mensaje}\n')

        f.write('\nTabla de simbolos:\n')
        f.write(f"{'nombre':<16}{'tipo':<10}{'mutable':<9}{'ambito':<8}linea\n")
        for s in estado.simbolos:
            tipo = s.tipo if s.tipo else '-'
            f.write(f"{s.nombre:<16}{tipo:<10}{'var' if s.mutable else 'val':<9}"
                    f"{s.ambito:<8}{s.linea}\n")

        if err_lex or err_sint:
            f.write(f'\nNota: el archivo tiene {len(err_lex)} errores lexicos y '
                    f'{len(err_sint)} errores sintacticos (ver log sintactico)\n')
        if errores:
            f.write(f'\nResultado: {len(errores)} errores semanticos\n')
        else:
            f.write('\nResultado: analisis semantico correcto\n')
    return nombre


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Uso: python semantico.py <archivo.kt> <usuarioGit>')
        sys.exit(1)

    archivo, usuario = sys.argv[1], sys.argv[2]
    with open(archivo, encoding='utf-8') as f:
        codigo = f.read()

    err_lex, err_sint, _ = analizar_sintaxis(codigo)
    for linea, categoria, mensaje in sorted(estado.errores_sem, key=lambda e: e[0]):
        print(f'Error semántico [{categoria}] (línea {linea}): {mensaje}')

    log = guardar_log(archivo, usuario, err_lex, err_sint)
    if not estado.errores_sem:
        print('Analisis semantico correcto')
    print(f'{len(estado.errores_sem)} errores semanticos. Log guardado en {log}')
