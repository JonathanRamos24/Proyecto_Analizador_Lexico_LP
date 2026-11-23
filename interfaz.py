# interfaz.py
# KotLex - Interfaz grafica (Tkinter)
# Lenguajes de Programacion
#
# Uso:   python interfaz.py
#
# Editor con numeros de linea, botones para cada analisis (lexico, sintactico
# y semantico) o los tres a la vez, y un panel con pestañas para ver los
# tokens, los errores, las reglas reconocidas, la tabla de simbolos y el log.
# Usa las mismas funciones que los programas de consola, asi que los logs
# que genera son los mismos (logs/lexico-..., logs/sintactico-..., logs/semantico-...).

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# los logs se guardan en la carpeta logs/ del proyecto
CARPETA = os.path.dirname(os.path.abspath(__file__))
os.chdir(CARPETA)

import lexer
import estado
import parser as analizador
import semantico
from lexer import crear_lexer, reserved

DESARROLLADORES = ['JonathanRamos24', 'magselpad', 'williamp11']

# colores (el rojo solo se usa para errores)
BORDE = '#a0a0a0'
ROJO = '#c62828'
ROJO_SUAVE = '#fdecec'
GRIS = '#8a8f98'

FUENTE = ('Segoe UI', 10)
FUENTE_NEGRITA = ('Segoe UI', 10, 'bold')
FUENTE_CODIGO = ('Consolas', 11)

PALABRAS = set(reserved.values()) - {'PRINT', 'PRINTLN', 'READLN',
                                     'LISTOF', 'MAPOF', 'SETOF'}
FUNCIONES = {'PRINT', 'PRINTLN', 'READLN', 'LISTOF', 'MAPOF', 'SETOF'}
NUMEROS = {'INT_LIT', 'LONG_LIT', 'DOUBLE_LIT', 'FLOAT_LIT'}
TEXTOS = {'STRING_LIT', 'CHAR_LIT'}


# ------------------------------------------------------------
# Editor con numeros de linea
# ------------------------------------------------------------
class Editor(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre, bg='white')
        self.lineas_error = set()

        self.numeros = tk.Canvas(self, width=46, bg='#f7f7f9',
                                 highlightthickness=0)
        self.texto = tk.Text(self, font=FUENTE_CODIGO, wrap='none', undo=True,
                             relief='flat', padx=8, pady=6,
                             insertbackground='black', tabs=('1c',))
        barra_y = ttk.Scrollbar(self, orient='vertical', command=self._mover)
        barra_x = ttk.Scrollbar(self, orient='horizontal',
                                command=self.texto.xview)
        self.texto.configure(yscrollcommand=lambda a, b: self._al_mover(barra_y, a, b),
                             xscrollcommand=barra_x.set)

        self.numeros.grid(row=0, column=0, sticky='ns')
        self.texto.grid(row=0, column=1, sticky='nsew')
        barra_y.grid(row=0, column=2, sticky='ns')
        barra_x.grid(row=1, column=1, sticky='ew')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # colores del codigo
        self.texto.tag_configure('palabra', foreground='#1f3fbf',
                                 font=('Consolas', 11, 'bold'))
        self.texto.tag_configure('funcion', foreground='black')
        self.texto.tag_configure('numero', foreground='#0b7285')
        self.texto.tag_configure('cadena', foreground='#2b8a3e')
        self.texto.tag_configure('comentario', foreground=GRIS,
                                 font=('Consolas', 11, 'italic'))
        self.texto.tag_configure('linea_error', background=ROJO_SUAVE)
        self.texto.tag_configure('marcada', background='#fff3bf')
        self.texto.tag_raise('cadena')
        self.texto.tag_raise('comentario')

        self._pendiente = None
        self.texto.bind('<KeyRelease>', self._al_escribir)
        self.texto.bind('<Configure>', lambda e: self.dibujar_numeros())

    def _mover(self, *args):
        self.texto.yview(*args)
        self.dibujar_numeros()

    def _al_mover(self, barra, a, b):
        barra.set(a, b)
        self.dibujar_numeros()

    def _al_escribir(self, _evento=None):
        self.dibujar_numeros()
        # se colorea un momento despues de dejar de escribir
        if self._pendiente:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(300, self.colorear)

    def dibujar_numeros(self):
        c = self.numeros
        c.delete('all')
        i = self.texto.index('@0,0')
        while True:
            info = self.texto.dlineinfo(i)
            if info is None:
                break
            y = info[1]
            n = int(i.split('.')[0])
            if n in self.lineas_error:
                c.create_rectangle(0, y, 4, y + info[3], fill=ROJO, outline='')
                color = ROJO
            else:
                color = GRIS
            c.create_text(38, y + 2, anchor='ne', text=str(n),
                          font=('Consolas', 10), fill=color)
            siguiente = self.texto.index(f'{i}+1line')
            if siguiente == i:
                break
            i = siguiente

    def codigo(self):
        return self.texto.get('1.0', 'end-1c')

    def poner_codigo(self, codigo):
        self.texto.delete('1.0', 'end')
        self.texto.insert('1.0', codigo)
        self.texto.edit_reset()
        self.marcar_errores(set())
        self.colorear()

    # resaltado de sintaxis usando el mismo lexer del proyecto
    def colorear(self):
        codigo = self.codigo()
        for tag in ('palabra', 'funcion', 'numero', 'cadena', 'comentario'):
            self.texto.tag_remove(tag, '1.0', 'end')

        lex = crear_lexer()
        lex.input(codigo)
        while True:
            tok = lex.token()
            if not tok:
                break
            if tok.type in PALABRAS:
                tag = 'palabra'
            elif tok.type in FUNCIONES:
                tag = 'funcion'
            elif tok.type in NUMEROS:
                tag = 'numero'
            elif tok.type in TEXTOS:
                tag = 'cadena'
            else:
                continue
            self.texto.tag_add(tag, f'1.0+{tok.lexpos}c', f'1.0+{lex.lexpos}c')

        # el lexer ignora los comentarios, se buscan aparte
        for m in re.finditer(r'//[^\n]*|/\*.*?\*/', codigo, re.S):
            self.texto.tag_add('comentario', f'1.0+{m.start()}c',
                               f'1.0+{m.end()}c')

    def marcar_errores(self, lineas):
        self.lineas_error = set(lineas)
        self.texto.tag_remove('linea_error', '1.0', 'end')
        for n in self.lineas_error:
            self.texto.tag_add('linea_error', f'{n}.0', f'{n}.0+1line')
        self.dibujar_numeros()

    def ir_a_linea(self, n):
        self.texto.tag_remove('marcada', '1.0', 'end')
        self.texto.tag_add('marcada', f'{n}.0', f'{n}.0+1line')
        self.texto.see(f'{n}.0')
        self.texto.mark_set('insert', f'{n}.0')
        self.texto.focus_set()
        self.dibujar_numeros()


# ------------------------------------------------------------
# Ventana principal
# ------------------------------------------------------------
class KotLex(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('KotLex - Analizador de Kotlin con PLY')
        self.geometry('1320x780')
        self.minsize(980, 600)
        self.archivo = None
        self.mensajes = {}      # fila de la tabla de errores -> mensaje completo

        self._estilos()
        self._menu()
        self._barra_herramientas()
        self._paneles()
        self._barra_estado()

        self.bind('<F5>', lambda e: self.analisis_lexico())
        self.bind('<F6>', lambda e: self.analisis_sintactico())
        self.bind('<F7>', lambda e: self.analisis_semantico())
        self.bind('<F8>', lambda e: self.analizar_todo())
        self.bind('<Control-o>', lambda e: self.abrir())
        self.bind('<Control-s>', lambda e: self.guardar())

        self.editor.poner_codigo('// Escriba aqui su codigo Kotlin o abra un archivo .kt\n'
                                 'fun main() {\n    println("Hola KotLex")\n}\n')

    # ---------- estilos ----------
    def _estilos(self):
        s = ttk.Style(self)
        if 'vista' in s.theme_names():
            s.theme_use('vista')          # aspecto normal de Windows
        s.configure('Todo.TButton', font=FUENTE_NEGRITA)
        s.configure('Treeview', font=('Consolas', 10), rowheight=22)
        s.configure('Treeview.Heading', font=FUENTE_NEGRITA)

    # ---------- menu ----------
    def _menu(self):
        barra = tk.Menu(self)
        m = tk.Menu(barra, tearoff=0)
        m.add_command(label='Abrir .kt...', accelerator='Ctrl+O', command=self.abrir)
        m.add_command(label='Guardar', accelerator='Ctrl+S', command=self.guardar)
        m.add_command(label='Limpiar', command=self.limpiar)
        m.add_separator()
        m.add_command(label='Salir', command=self.destroy)
        barra.add_cascade(label='Archivo', menu=m)

        m = tk.Menu(barra, tearoff=0)
        m.add_command(label='Deshacer', accelerator='Ctrl+Z',
                      command=lambda: self.editor.texto.event_generate('<<Undo>>'))
        m.add_command(label='Rehacer', accelerator='Ctrl+Y',
                      command=lambda: self.editor.texto.event_generate('<<Redo>>'))
        barra.add_cascade(label='Editar', menu=m)

        m = tk.Menu(barra, tearoff=0)
        m.add_command(label='Léxico', accelerator='F5', command=self.analisis_lexico)
        m.add_command(label='Sintáctico', accelerator='F6', command=self.analisis_sintactico)
        m.add_command(label='Semántico', accelerator='F7', command=self.analisis_semantico)
        m.add_command(label='Analizar todo', accelerator='F8', command=self.analizar_todo)
        barra.add_cascade(label='Análisis', menu=m)

        m = tk.Menu(barra, tearoff=0)
        m.add_command(label='Abrir carpeta de logs',
                      command=lambda: os.startfile(os.path.join(CARPETA, 'logs')))
        barra.add_cascade(label='Logs', menu=m)

        m = tk.Menu(barra, tearoff=0)
        m.add_command(label='Acerca de KotLex', command=self.acerca_de)
        barra.add_cascade(label='Ayuda', menu=m)
        self.config(menu=barra)

    # ---------- botones ----------
    def _barra_herramientas(self):
        f = ttk.Frame(self, padding=(8, 6))
        f.pack(fill='x')
        ttk.Button(f, text='Abrir .kt',
                   command=self.abrir).pack(side='left', padx=(0, 3))
        ttk.Button(f, text='Guardar',
                   command=self.guardar).pack(side='left', padx=3)
        ttk.Button(f, text='Limpiar',
                   command=self.limpiar).pack(side='left', padx=3)
        ttk.Separator(f, orient='vertical').pack(side='left', fill='y', padx=8)
        ttk.Button(f, text='Léxico (F5)',
                   command=self.analisis_lexico).pack(side='left', padx=3)
        ttk.Button(f, text='Sintáctico (F6)',
                   command=self.analisis_sintactico).pack(side='left', padx=3)
        ttk.Button(f, text='Semántico (F7)',
                   command=self.analisis_semantico).pack(side='left', padx=3)
        ttk.Button(f, text='Analizar todo (F8)', style='Todo.TButton',
                   command=self.analizar_todo).pack(side='left', padx=3)

        self.desarrollador = tk.StringVar(value=DESARROLLADORES[0])
        caja = ttk.Combobox(f, textvariable=self.desarrollador, width=18,
                            values=DESARROLLADORES, state='readonly')
        caja.pack(side='right')
        ttk.Label(f, text='Desarrollador:').pack(side='right', padx=6)

    # ---------- editor y resultados ----------
    def _paneles(self):
        panel = ttk.PanedWindow(self, orient='horizontal')
        panel.pack(fill='both', expand=True, padx=8)

        # izquierda: editor
        izq = tk.Frame(panel, bg='white', highlightbackground=BORDE,
                       highlightthickness=1)
        cab = tk.Frame(izq, bg='white')
        cab.pack(fill='x', padx=10, pady=(8, 4))
        tk.Label(cab, text='Editor', font=FUENTE_NEGRITA, bg='white').pack(side='left')
        self.lbl_archivo = tk.Label(cab, text='sin guardar', fg=GRIS, bg='white')
        self.lbl_archivo.pack(side='left', padx=8)
        ttk.Separator(izq).pack(fill='x')
        self.editor = Editor(izq)
        self.editor.pack(fill='both', expand=True)
        panel.add(izq, weight=1)

        # derecha: pestañas
        der = tk.Frame(panel, bg='white', highlightbackground=BORDE,
                       highlightthickness=1)
        self.pestanas = ttk.Notebook(der)
        self.pestanas.pack(fill='both', expand=True)

        self.t_tokens = self._tabla(('#', 'Línea', 'Col', 'Tipo de token', 'Lexema'),
                                    (50, 60, 50, 150, 200))
        self.t_errores = self._tabla(('Tipo', 'Línea', 'Mensaje'), (95, 55, 520))
        self.t_reglas = self._tabla(('Construcción reconocida', 'Veces'), (300, 80))
        self.t_simbolos = self._tabla(('Nombre', 'Tipo', 'Mutable', 'Ámbito', 'Línea'),
                                      (150, 100, 80, 70, 60))
        self.t_errores.bind('<<TreeviewSelect>>', self._error_elegido)

        caja_log = ttk.Frame(self.pestanas)
        self.txt_log = tk.Text(caja_log, font=('Consolas', 10), relief='flat',
                               padx=10, pady=8, wrap='none', state='disabled')
        self.txt_log.pack(fill='both', expand=True)

        self.pestanas.add(self.t_tokens.master, text='Tokens')
        self.pestanas.add(self.t_errores.master, text='Errores')
        self.pestanas.add(self.t_reglas.master, text='Reglas')
        self.pestanas.add(self.t_simbolos.master, text='Tabla de símbolos')
        self.pestanas.add(caja_log, text='Log')

        # mensaje del error elegido (o del primero)
        self.lbl_detalle = tk.Label(der, text='', anchor='w', justify='left',
                                    font=FUENTE, bg='white', padx=12, pady=10,
                                    wraplength=560)
        self.lbl_detalle.pack(fill='x')
        panel.add(der, weight=1)

    def _tabla(self, columnas, anchos):
        marco = ttk.Frame(self.pestanas)
        t = ttk.Treeview(marco, columns=columnas, show='headings')
        for col, ancho in zip(columnas, anchos):
            t.heading(col, text=col, anchor='w')
            t.column(col, width=ancho, anchor='w', stretch=(col == columnas[-1]))
        barra = ttk.Scrollbar(marco, orient='vertical', command=t.yview)
        t.configure(yscrollcommand=barra.set)
        t.pack(side='left', fill='both', expand=True)
        barra.pack(side='right', fill='y')
        t.tag_configure('error', background=ROJO_SUAVE, foreground=ROJO)
        t.tag_configure('par', background='#fafbfc')
        return t

    def _barra_estado(self):
        f = tk.Frame(self, bd=1, relief='sunken')
        f.pack(fill='x', side='bottom', pady=(6, 0))
        self.lbl_estado = tk.Label(f, text='Listo', padx=8, pady=3)
        self.lbl_estado.pack(side='left')
        self.lbl_ok = tk.Label(f, text='', padx=8)
        self.lbl_ok.pack(side='left')
        self.lbl_mal = tk.Label(f, text='', fg=ROJO, padx=8)
        self.lbl_mal.pack(side='left')
        self.lbl_log = tk.Label(f, text='', padx=8)
        self.lbl_log.pack(side='right')

    # ------------------------------------------------------------
    # Archivo
    # ------------------------------------------------------------
    def abrir(self):
        ruta = filedialog.askopenfilename(
            initialdir=CARPETA, title='Abrir archivo Kotlin',
            filetypes=[('Kotlin', '*.kt *.kts'), ('Todos', '*.*')])
        if not ruta:
            return
        with open(ruta, encoding='utf-8') as f:
            self.editor.poner_codigo(f.read())
        self.archivo = ruta
        self.lbl_archivo.config(text=os.path.basename(ruta))
        self._limpiar_resultados()
        self.lbl_estado.config(text=f'Archivo abierto: {os.path.basename(ruta)}')

    def guardar(self):
        if not self.archivo:
            ruta = filedialog.asksaveasfilename(
                initialdir=CARPETA, defaultextension='.kt',
                filetypes=[('Kotlin', '*.kt')])
            if not ruta:
                return
            self.archivo = ruta
            self.lbl_archivo.config(text=os.path.basename(ruta))
        with open(self.archivo, 'w', encoding='utf-8') as f:
            f.write(self.editor.codigo())
        self.lbl_estado.config(text='Archivo guardado')

    def limpiar(self):
        self.editor.poner_codigo('')
        self.archivo = None
        self.lbl_archivo.config(text='sin guardar')
        self._limpiar_resultados()
        self.lbl_estado.config(text='Listo')

    def acerca_de(self):
        messagebox.showinfo(
            'Acerca de KotLex',
            'KotLex - Analizador léxico, sintáctico y semántico de Kotlin\n'
            'hecho con Python y PLY.\n\n'
            'Lenguajes de Programación - ESPOL\n'
            'Jonathan Ramos, Miguel Galarza y William Pacalla')

    # nombre que aparece en el log
    def _nombre_archivo(self):
        if not self.archivo:
            return 'editor (sin guardar)'
        try:
            return os.path.relpath(self.archivo, CARPETA).replace('\\', '/')
        except ValueError:
            return self.archivo

    # ------------------------------------------------------------
    # Resultados
    # ------------------------------------------------------------
    def _limpiar_resultados(self):
        for t in (self.t_tokens, self.t_errores, self.t_reglas, self.t_simbolos):
            t.delete(*t.get_children())
        self._poner_log('')
        self.editor.marcar_errores(set())
        self.lbl_detalle.config(text='', bg='white')
        self.lbl_ok.config(text='')
        self.lbl_mal.config(text='')
        self.lbl_log.config(text='')
        self.pestanas.tab(0, text='Tokens')
        self.pestanas.tab(1, text='Errores')

    def _poner_log(self, ruta_o_vacio):
        self.txt_log.config(state='normal')
        self.txt_log.delete('1.0', 'end')
        if ruta_o_vacio:
            with open(ruta_o_vacio, encoding='utf-8') as f:
                self.txt_log.insert('1.0', f.read())
        self.txt_log.config(state='disabled')

    def _llenar_tokens(self, codigo):
        resultado, errores = lexer.analizar(codigo)
        t = self.t_tokens
        t.delete(*t.get_children())
        filas = [(l, c, tipo, valor, '') for l, c, tipo, valor in resultado]
        filas += [(l, c, 'ERROR', ch, 'error') for l, c, ch, _ in errores]
        filas.sort(key=lambda f: (f[0], f[1]))
        for i, (l, c, tipo, valor, tag) in enumerate(filas, 1):
            tags = (tag,) if tag else (('par',) if i % 2 == 0 else ())
            t.insert('', 'end', values=(i, l, c, tipo, valor), tags=tags)
        self.pestanas.tab(0, text=f'Tokens ({len(resultado)})')
        return resultado, errores

    def _llenar_errores(self, errores):
        # errores: lista de (tipo, linea, mensaje)
        t = self.t_errores
        t.delete(*t.get_children())
        self.mensajes = {}
        for tipo, linea, msg in errores:
            # en la tabla no se repite "Error ... (linea N, col. M):"
            m = re.match(r'Error \S+ (\[[^\]]+\] )?\(línea \d+(?:, col\. \d+)?\):\s*', msg)
            corto = (m.group(1) or '') + msg[m.end():] if m else msg
            fila = t.insert('', 'end', values=(tipo, linea, corto), tags=('error',))
            self.mensajes[fila] = msg
        self.pestanas.tab(1, text=f'Errores ({len(errores)})' if errores else 'Errores')
        self.editor.marcar_errores({e[1] for e in errores})
        if errores:
            self.lbl_detalle.config(text=errores[0][2], fg=ROJO, bg=ROJO_SUAVE)
        else:
            self.lbl_detalle.config(text='No se encontraron errores.',
                                    fg='black', bg='white')

    def _error_elegido(self, _evento):
        sel = self.t_errores.selection()
        if not sel:
            return
        linea = self.t_errores.item(sel[0], 'values')[1]
        self.lbl_detalle.config(text=self.mensajes[sel[0]], fg=ROJO, bg=ROJO_SUAVE)
        self.editor.ir_a_linea(int(linea))

    def _llenar_reglas(self, construcciones):
        t = self.t_reglas
        t.delete(*t.get_children())
        for i, nombre in enumerate(sorted(construcciones), 1):
            t.insert('', 'end', values=(nombre, construcciones[nombre]),
                     tags=(('par',) if i % 2 == 0 else ()))

    def _llenar_simbolos(self):
        t = self.t_simbolos
        t.delete(*t.get_children())
        for i, s in enumerate(estado.simbolos, 1):
            t.insert('', 'end', values=(s.nombre, s.tipo or '-',
                                        'var' if s.mutable else 'val',
                                        s.ambito, s.linea),
                     tags=(('par',) if i % 2 == 0 else ()))

    def _estado(self, texto, ok, mal, logs):
        self.lbl_estado.config(text=texto)
        self.lbl_ok.config(text=ok)
        self.lbl_mal.config(text=mal)
        if len(logs) == 1:
            self.lbl_log.config(text='Log: ' + logs[0])
        else:
            self.lbl_log.config(text='Logs: ' + '   '.join(os.path.basename(l) for l in logs))
        self._poner_log(logs[-1])

    # ------------------------------------------------------------
    # Analisis
    # ------------------------------------------------------------
    @staticmethod
    def _errores_lexicos(err_lex):
        return [('Léxico', l, msg) for l, c, ch, msg in err_lex]

    def analisis_lexico(self):
        codigo = self.editor.codigo()
        usuario = self.desarrollador.get()
        resultado, errores = self._llenar_tokens(codigo)
        self._llenar_errores(self._errores_lexicos(errores))
        log = lexer.guardar_log(self._nombre_archivo(), usuario, resultado, errores)
        self._estado('Análisis léxico terminado',
                     f'{len(resultado)} tokens válidos',
                     f'{len(errores)} errores' if errores else '', [log])
        self.pestanas.select(1 if errores else 0)

    def analisis_sintactico(self):
        codigo = self.editor.codigo()
        usuario = self.desarrollador.get()
        self._llenar_tokens(codigo)
        err_lex, err_sint, construcciones = analizador.analizar_sintaxis(codigo)
        errores = self._errores_lexicos(err_lex)
        errores += [('Sintáctico', l, msg) for l, c, msg in err_sint]
        self._llenar_errores(errores)
        self._llenar_reglas(construcciones)
        log = analizador.guardar_log(self._nombre_archivo(), usuario,
                                     err_lex, err_sint, construcciones)
        self._estado('Análisis sintáctico terminado',
                     f'{sum(construcciones.values())} construcciones reconocidas',
                     f'{len(errores)} errores' if errores else '', [log])
        self.pestanas.select(1 if errores else 2)

    def analisis_semantico(self):
        codigo = self.editor.codigo()
        usuario = self.desarrollador.get()
        self._llenar_tokens(codigo)
        err_lex, err_sint, construcciones = analizador.analizar_sintaxis(codigo)
        errores = [('Semántico', l, f'Error semántico [{cat}] (línea {l}): {msg}')
                   for l, cat, msg in sorted(estado.errores_sem, key=lambda e: e[0])]
        self._llenar_errores(errores)
        self._llenar_reglas(construcciones)
        self._llenar_simbolos()
        log = semantico.guardar_log(self._nombre_archivo(), usuario, err_lex, err_sint)
        aviso = ''
        if err_lex or err_sint:
            aviso = f' (además hay {len(err_lex) + len(err_sint)} errores léxicos/sintácticos)'
        self._estado('Análisis semántico terminado' + aviso,
                     f'{len(estado.simbolos)} símbolos en la tabla',
                     f'{len(errores)} errores semánticos' if errores else '', [log])
        self.pestanas.select(1 if errores else 3)

    # los tres analisis seguidos, con su log cada uno
    def analizar_todo(self):
        codigo = self.editor.codigo()
        usuario = self.desarrollador.get()
        nombre = self._nombre_archivo()

        resultado, err_lex = self._llenar_tokens(codigo)
        log_lex = lexer.guardar_log(nombre, usuario, resultado, err_lex)

        err_lex2, err_sint, construcciones = analizador.analizar_sintaxis(codigo)
        log_sint = analizador.guardar_log(nombre, usuario, err_lex2, err_sint,
                                          construcciones)
        log_sem = semantico.guardar_log(nombre, usuario, err_lex2, err_sint)

        errores = self._errores_lexicos(err_lex)
        errores += [('Sintáctico', l, msg) for l, c, msg in err_sint]
        errores += [('Semántico', l, f'Error semántico [{cat}] (línea {l}): {msg}')
                    for l, cat, msg in sorted(estado.errores_sem, key=lambda e: e[0])]
        errores.sort(key=lambda e: e[1])
        self._llenar_errores(errores)
        self._llenar_reglas(construcciones)
        self._llenar_simbolos()

        partes = []
        if err_lex:
            partes.append(f'{len(err_lex)} léxicos')
        if err_sint:
            partes.append(f'{len(err_sint)} sintácticos')
        if estado.errores_sem:
            partes.append(f'{len(estado.errores_sem)} semánticos')
        self._estado('Análisis completo terminado',
                     f'{len(resultado)} tokens válidos',
                     ('Errores: ' + ', '.join(partes)) if partes else '',
                     [log_lex, log_sint, log_sem])
        self.pestanas.select(1 if errores else 0)


if __name__ == '__main__':
    try:
        # para que no se vea borroso en pantallas con escala (Windows)
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    KotLex().mainloop()
