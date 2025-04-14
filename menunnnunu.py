import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
from scipy.stats import chi2, kstwobign, norm
from math import sqrt
from collections import defaultdict
from tabulate import tabulate
import math

class GeneradorNumerosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Números Pseudoaleatorios")
        self.root.geometry("1000x700")
        
        # Configuración de estilo
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))
        
        # Variables de estado
        self.numeros_generados = []
        self.tabla_generacion = ""
        self.tabla_prueba = ""
        self.resultados_prueba = ""
        
        # Lista de pruebas disponibles
        self.pruebas_disponibles = [
            "Chi-cuadrada", 
            "Kolmogorov-Smirnov", 
            "Arriba y abajo", 
            "Arriba y abajo de la media", 
            "Poker", 
            "Huecos"
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de generación
        self.setup_pestana_generacion()
        
        # Pestaña de pruebas
        self.setup_pestana_pruebas()
        
        # Pestaña de resultados
        self.setup_pestana_resultados()
        
        # Menú
        self.setup_menu()
    
    def setup_pestana_generacion(self):
        pestana = ttk.Frame(self.notebook)
        self.notebook.add(pestana, text="Generación")
        
        # Frame de parámetros
        frame_params = ttk.LabelFrame(pestana, text="Parámetros de Generación", padding=10)
        frame_params.pack(fill=tk.X, padx=10, pady=5)
        
        # Método de generación
        ttk.Label(frame_params, text="Método:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.metodo = tk.StringVar()
        metodos = ["Cuadrados Medios", "Productos Medios", "Constante Multiplicativa", "Congruencial Lineal"]
        combo = ttk.Combobox(frame_params, textvariable=self.metodo, values=metodos, state="readonly")
        combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        combo.current(0)
        combo.bind("<<ComboboxSelected>>", self.actualizar_campos_generacion)
        
        # Frame para campos específicos
        self.frame_campos = ttk.Frame(frame_params)
        self.frame_campos.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Botones
        frame_botones = ttk.Frame(frame_params)
        frame_botones.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(frame_botones, text="Generar", command=self.generar_numeros).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Ir a Pruebas", command=self.ir_a_pruebas).pack(side=tk.LEFT, padx=5)
        
        # Tabla de generación
        frame_tabla = ttk.LabelFrame(pestana, text="Tabla de Generación", padding=10)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_tabla_gen = scrolledtext.ScrolledText(
            frame_tabla, 
            wrap=tk.WORD, 
            height=12,
            font=('Courier New', 10),
            state=tk.DISABLED
        )
        self.texto_tabla_gen.pack(fill=tk.BOTH, expand=True)
        
        frame_params.columnconfigure(1, weight=1)
        self.actualizar_campos_generacion()
    
    def setup_pestana_pruebas(self):
        pestana = ttk.Frame(self.notebook)
        self.notebook.add(pestana, text="Pruebas")
    
        # Frame principal dividido
        main_frame = ttk.Frame(pestana)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Frame izquierdo para parámetros y tabla (75% del ancho)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
        # Frame de parámetros
        frame_params = ttk.LabelFrame(left_frame, text="Parámetros de Prueba", padding=10)
        frame_params.pack(fill=tk.X, padx=10, pady=5)
    
        # Frame derecho para información fija (25% del ancho)
        info_frame = ttk.LabelFrame(main_frame, text="Información de Pruebas", padding=10, width=300)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
        info_frame.pack_propagate(False)  # Fijar el ancho
    
        # Texto informativo fijo
        info_text = """PRUEBAS ESTADÍSTICAS

    Uniformidad:
    - Chi-cuadrada
    - Kolmogorov-Smirnov

    Independencia:
    - Arriba/abajo
    - Arriba/abajo media
    - Poker
    - Huecos

    Confianza típica: 95%
    Alpha = 1 - confianza"""
    
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, padding=10)
        info_label.pack(fill=tk.BOTH, expand=True)
    
        # Resto del código original para la parte izquierda...
        ttk.Label(frame_params, text="Prueba:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.prueba = tk.StringVar()
        self.combo_pruebas = ttk.Combobox(
            frame_params, 
            textvariable=self.prueba, 
            values=self.pruebas_disponibles,
            state="readonly"
        )
        self.combo_pruebas.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.combo_pruebas.current(0)
        self.combo_pruebas.bind("<<ComboboxSelected>>", self.actualizar_campos_prueba)
    
        # Frame para campos específicos
        self.frame_campos_prueba = ttk.Frame(frame_params)
        self.frame_campos_prueba.grid(row=1, column=0, columnspan=2, sticky="ew")
    
        # Botones
        frame_botones = ttk.Frame(frame_params)
        frame_botones.grid(row=2, column=0, columnspan=2, pady=10)
    
        ttk.Button(frame_botones, text="Ejecutar Prueba", command=self.ejecutar_prueba).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Ir a Resultados", command=self.ir_a_resultados).pack(side=tk.LEFT, padx=5)
    
        # Tabla de prueba
        frame_tabla = ttk.LabelFrame(left_frame, text="Tabla de Prueba", padding=10)
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
        self.texto_tabla_prueba = scrolledtext.ScrolledText(
            frame_tabla, 
            wrap=tk.WORD, 
            height=12,
            font=('Courier New', 10),
            state=tk.DISABLED
        )
        self.texto_tabla_prueba.pack(fill=tk.BOTH, expand=True)
    
        frame_params.columnconfigure(1, weight=1)
        self.actualizar_campos_prueba()
    
    def setup_pestana_resultados(self):
        pestana = ttk.Frame(self.notebook)
        self.notebook.add(pestana, text="Resultados")
        
        # Frame para números generados
        frame_gen = ttk.LabelFrame(pestana, text="Números Generados", padding=10)
        frame_gen.pack(fill=tk.BOTH, padx=10, pady=5)
        
        self.texto_resultados_gen = scrolledtext.ScrolledText(
            frame_gen, 
            wrap=tk.WORD, 
            height=8,
            font=('Courier New', 10),
            state=tk.DISABLED
        )
        self.texto_resultados_gen.pack(fill=tk.BOTH, expand=True)
        
        # Frame para resultados de prueba
        frame_prueba = ttk.LabelFrame(pestana, text="Resultados de Prueba", padding=10)
        frame_prueba.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.texto_resultados_prueba = scrolledtext.ScrolledText(
            frame_prueba, 
            wrap=tk.WORD,
            font=('Courier New', 10),
            state=tk.DISABLED
        )
        self.texto_resultados_prueba.pack(fill=tk.BOTH, expand=True)
        
        # Botón limpiar
        ttk.Button(pestana, text="Limpiar Resultados", command=self.limpiar_resultados).pack(pady=5)
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        
        self.root.config(menu=menubar)
    
    def actualizar_campos_generacion(self, event=None):
        # Limpiar frame
        for widget in self.frame_campos.winfo_children():
            widget.destroy()
        
        metodo = self.metodo.get()
        
        # Campos específicos del método (cantidad siempre al final)
        if metodo == "Cuadrados Medios":
            ttk.Label(self.frame_campos, text="Semilla:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            self.semilla = ttk.Entry(self.frame_campos)
            self.semilla.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            
        elif metodo == "Productos Medios":
            ttk.Label(self.frame_campos, text="Semilla 1:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            self.semilla1 = ttk.Entry(self.frame_campos)
            self.semilla1.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            
            ttk.Label(self.frame_campos, text="Semilla 2:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
            self.semilla2 = ttk.Entry(self.frame_campos)
            self.semilla2.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
            
        elif metodo == "Constante Multiplicativa":
            ttk.Label(self.frame_campos, text="Semilla:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            self.semilla = ttk.Entry(self.frame_campos)
            self.semilla.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            
            ttk.Label(self.frame_campos, text="Multiplicador:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
            self.multiplier = ttk.Entry(self.frame_campos)
            self.multiplier.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
            
        elif metodo == "Congruencial Lineal":
            ttk.Label(self.frame_campos, text="Semilla:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            self.semilla = ttk.Entry(self.frame_campos)
            self.semilla.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            
            ttk.Label(self.frame_campos, text="Multiplicador:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
            self.multiplier = ttk.Entry(self.frame_campos)
            self.multiplier.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
            
            ttk.Label(self.frame_campos, text="Incremento:").grid(row=2, column=0, padx=5, pady=2, sticky="e")
            self.incremento = ttk.Entry(self.frame_campos)
            self.incremento.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
            
            ttk.Label(self.frame_campos, text="Módulo:").grid(row=3, column=0, padx=5, pady=2, sticky="e")
            self.modulo = ttk.Entry(self.frame_campos)
            self.modulo.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        
        # Cantidad siempre al final
        ttk.Label(self.frame_campos, text="Cantidad:").grid(row=4, column=0, padx=5, pady=2, sticky="e")
        self.cantidad = ttk.Entry(self.frame_campos)
        self.cantidad.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        
        self.frame_campos.columnconfigure(1, weight=1)
    
    def actualizar_campos_prueba(self, event=None):
        # Limpiar frame
        for widget in self.frame_campos_prueba.winfo_children():
            widget.destroy()
        
        prueba = self.prueba.get()
        
        if prueba in ["Chi-cuadrada", "Kolmogorov-Smirnov", "Arriba y abajo", "Arriba y abajo de la media", "Poker"]:
            ttk.Label(self.frame_campos_prueba, text="Confianza (%):").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            self.confianza = ttk.Entry(self.frame_campos_prueba)
            self.confianza.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            self.confianza.insert(0, "95")
            
            if prueba == "Poker":
                ttk.Label(self.frame_campos_prueba, text="Dígitos (3-5):").grid(row=1, column=0, padx=5, pady=2, sticky="e")
                self.digitos = ttk.Entry(self.frame_campos_prueba)
                self.digitos.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
                self.digitos.insert(0, "5")
        
        elif prueba == "Huecos":
            ttk.Label(self.frame_campos_prueba, text="Límite inferior:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
            self.alpha = ttk.Entry(self.frame_campos_prueba)
            self.alpha.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
            self.alpha.insert(0, "0.3")
            
            ttk.Label(self.frame_campos_prueba, text="Límite superior:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
            self.beta = ttk.Entry(self.frame_campos_prueba)
            self.beta.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
            self.beta.insert(0, "0.7")
            
            ttk.Label(self.frame_campos_prueba, text="Confianza (%):").grid(row=2, column=0, padx=5, pady=2, sticky="e")
            self.confianza = ttk.Entry(self.frame_campos_prueba)
            self.confianza.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
            self.confianza.insert(0, "95")
        
        self.frame_campos_prueba.columnconfigure(1, weight=1)
    
    def validar_positivo(self, valor, nombre):
        try:
            num = int(valor)
            if num <= 0:
                raise ValueError(f"{nombre} debe ser mayor que 0")
            return num
        except ValueError:
            raise ValueError(f"{nombre} debe ser un número entero positivo")
    
    def validar_no_negativo(self, valor, nombre):
        try:
            num = float(valor)
            if num < 0:
                raise ValueError(f"{nombre} no puede ser negativo")
            return num
        except ValueError:
            raise ValueError(f"{nombre} debe ser un número no negativo")
    
    def generar_numeros(self):
        metodo = self.metodo.get()
        
        try:
            # Validar y obtener parámetros
            n = self.validar_positivo(self.cantidad.get(), "Cantidad de números")
            if n <= 1:
                raise ValueError("La cantidad de números a generar debe ser mayor que 1")
            
            # Verificar disponibilidad de Kolmogorov-Smirnov
            if n <= 30 and "Kolmogorov-Smirnov" not in self.pruebas_disponibles:
                self.pruebas_disponibles.insert(1, "Kolmogorov-Smirnov")
                self.combo_pruebas['values'] = self.pruebas_disponibles
            elif n > 30 and "Kolmogorov-Smirnov" in self.pruebas_disponibles:
                self.pruebas_disponibles.remove("Kolmogorov-Smirnov")
                self.combo_pruebas['values'] = self.pruebas_disponibles
                if self.prueba.get() == "Kolmogorov-Smirnov":
                    self.prueba.set(self.pruebas_disponibles[0])
            
            # Generar números según el método seleccionado
            if metodo == "Cuadrados Medios":
                semilla = self.validar_positivo(self.semilla.get(), "Semilla")
                self.numeros_generados, self.tabla_generacion = self.metodo_cuadrados_medios(semilla, n)
                
            elif metodo == "Productos Medios":
                semilla1 = self.validar_positivo(self.semilla1.get(), "Semilla 1")
                semilla2 = self.validar_positivo(self.semilla2.get(), "Semilla 2")
                self.numeros_generados, self.tabla_generacion = self.metodo_productos_medios(semilla1, semilla2, n)
                
            elif metodo == "Constante Multiplicativa":
                semilla = self.validar_positivo(self.semilla.get(), "Semilla")
                multiplier = self.validar_positivo(self.multiplier.get(), "Multiplicador")
                self.numeros_generados, self.tabla_generacion = self.metodo_constante_multiplicativa(semilla, multiplier, n)
                
            elif metodo == "Congruencial Lineal":
                semilla = self.validar_positivo(self.semilla.get(), "Semilla")
                multiplier = self.validar_positivo(self.multiplier.get(), "Multiplicador")
                incremento = self.validar_no_negativo(self.incremento.get(), "Incremento")
                modulo = self.validar_positivo(self.modulo.get(), "Módulo")
                self.numeros_generados, self.tabla_generacion = self.metodo_lineal(semilla, multiplier, incremento, modulo, n)
            
            # Mostrar resultados
            self.mostrar_tabla_generacion()
            messagebox.showinfo("Éxito", "Números generados correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar números: {str(e)}")
    
    def ejecutar_prueba(self):
        if not self.numeros_generados:
            messagebox.showwarning("Advertencia", "Primero genere números aleatorios")
            return
        
        prueba = self.prueba.get()
        
        try:
            confianza = self.validar_no_negativo(self.confianza.get(), "Confianza")
            if confianza <= 1 or confianza > 99:
                raise ValueError("Confianza debe estar entre 0 y 100")
            confianza = confianza / 100
            
            if prueba == "Chi-cuadrada":
                self.tabla_prueba, self.resultados_prueba = self.prueba_chi_cuadrada(self.numeros_generados, confianza)
                
            elif prueba == "Kolmogorov-Smirnov":
                if len(self.numeros_generados) > 30:
                    messagebox.showwarning("Advertencia", "Kolmogorov-Smirnov solo puede usarse con 30 números o menos")
                    return
                self.tabla_prueba, self.resultados_prueba = self.prueba_kolmogorov(self.numeros_generados, confianza)
                
            elif prueba == "Arriba y abajo":
                self.tabla_prueba, self.resultados_prueba = self.prueba_arriba_abajo(self.numeros_generados, confianza)
                
            elif prueba == "Arriba y abajo de la media":
                self.tabla_prueba, self.resultados_prueba = self.prueba_arriba_debajo_media(self.numeros_generados, confianza)
                
            elif prueba == "Poker":
                digitos = self.validar_positivo(self.digitos.get(), "Dígitos")
                if digitos not in [3, 4, 5]:
                    raise ValueError("Dígitos debe ser 3, 4 o 5")
                self.tabla_prueba, self.resultados_prueba = self.prueba_poker(self.numeros_generados, confianza, digitos)
                
            elif prueba == "Huecos":
                alpha = self.validar_no_negativo(self.alpha.get(), "Límite inferior")
                beta = self.validar_no_negativo(self.beta.get(), "Límite superior")
                if alpha <= 0 or alpha >= 1:
                    raise ValueError("El límite inferior (alpha) debe estar entre 0 y 1 (ejemplo: 0.1 - 0.9)")
                if beta <= 0 or beta >= 1:
                    raise ValueError("El límite superior (beta) debe estar entre 0 y 1 (ejemplo: 0.1 - 0.9)")
                if alpha >= beta:
                    raise ValueError("El límite inferior debe ser menor que el superior")
                self.tabla_prueba, self.resultados_prueba = self.prueba_huecos(self.numeros_generados, alpha, beta, confianza)
            
            # Mostrar resultados
            self.mostrar_tabla_prueba()
            self.mostrar_resultados_completos()
            messagebox.showinfo("Éxito", "Prueba ejecutada correctamente")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la prueba: {str(e)}")
    
    def mostrar_tabla_generacion(self):
        self.texto_tabla_gen.config(state=tk.NORMAL)
        self.texto_tabla_gen.delete(1.0, tk.END)
        self.texto_tabla_gen.insert(tk.END, self.tabla_generacion)
        self.texto_tabla_gen.config(state=tk.DISABLED)
        
        # Mostrar también en resultados
        self.texto_resultados_gen.config(state=tk.NORMAL)
        self.texto_resultados_gen.delete(1.0, tk.END)
        self.texto_resultados_gen.insert(tk.END, "=== TABLA DE GENERACIÓN ===\n\n")
        self.texto_resultados_gen.insert(tk.END, self.tabla_generacion)
        self.texto_resultados_gen.config(state=tk.DISABLED)
    
    def mostrar_tabla_prueba(self):
        self.texto_tabla_prueba.config(state=tk.NORMAL)
        self.texto_tabla_prueba.delete(1.0, tk.END)
        self.texto_tabla_prueba.insert(tk.END, self.tabla_prueba)
        self.texto_tabla_prueba.config(state=tk.DISABLED)
    
    def mostrar_resultados_completos(self):
        self.texto_resultados_prueba.config(state=tk.NORMAL)
        self.texto_resultados_prueba.delete(1.0, tk.END)
        self.texto_resultados_prueba.insert(tk.END, "=== RESULTADOS DE PRUEBA ===\n\n")
        self.texto_resultados_prueba.insert(tk.END, self.tabla_prueba)
        self.texto_resultados_prueba.insert(tk.END, "\n\n=== DETALLES ESTADÍSTICOS ===\n\n")
        self.texto_resultados_prueba.insert(tk.END, self.resultados_prueba)
        self.texto_resultados_prueba.config(state=tk.DISABLED)
    
    def limpiar_resultados(self):
        # Limpiar pestaña de generación
        self.texto_tabla_gen.config(state=tk.NORMAL)
        self.texto_tabla_gen.delete(1.0, tk.END)
        self.texto_tabla_gen.config(state=tk.DISABLED)
        
        # Limpiar pestaña de pruebas
        self.texto_tabla_prueba.config(state=tk.NORMAL)
        self.texto_tabla_prueba.delete(1.0, tk.END)
        self.texto_tabla_prueba.config(state=tk.DISABLED)
        
        # Limpiar pestaña de resultados
        self.texto_resultados_gen.config(state=tk.NORMAL)
        self.texto_resultados_gen.delete(1.0, tk.END)
        self.texto_resultados_gen.config(state=tk.DISABLED)
        
        self.texto_resultados_prueba.config(state=tk.NORMAL)
        self.texto_resultados_prueba.delete(1.0, tk.END)
        self.texto_resultados_prueba.config(state=tk.DISABLED)
        
        # Reiniciar variables
        self.numeros_generados = []
        self.tabla_generacion = ""
        self.tabla_prueba = ""
        self.resultados_prueba = ""
        
        messagebox.showinfo("Información", "Resultados limpiados correctamente")
    
    def ir_a_pruebas(self):
        if not self.numeros_generados:
            messagebox.showwarning("Advertencia", "Primero genere números aleatorios")
            return
        self.notebook.select(1)  # Ir a pestaña de pruebas
    
    def ir_a_resultados(self):
        if not hasattr(self, 'resultados_prueba') or not self.resultados_prueba:
            messagebox.showwarning("Advertencia", "Primero ejecute una prueba estadística")
            return
        self.notebook.select(2)  # Ir a pestaña de resultados
    
    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", 
                          "Generador de Números Pseudoaleatorios\n"
                          "Versión 2.0\n\n"
                          "Características:\n"
                          "- 4 métodos de generación\n"
                          "- 6 pruebas estadísticas\n"
                          "- Kolmogorov-Smirnov para n ≤ 30\n"
                          "- Interfaz mejorada")
    
    # Métodos de generación de números pseudoaleatorios
    def metodo_cuadrados_medios(self, semilla, n):
        longitud = len(str(semilla))
        if longitud % 2 != 0:
            raise ValueError("La semilla debe tener longitud par")
        
        numeros = []
        tabla = []
        
        for i in range(1, n + 1):
            cuadrado = semilla * semilla
            str_cuadrado = str(cuadrado).zfill(longitud * 2)
            inicio = (len(str_cuadrado) - longitud) // 2
            fin = inicio + longitud
            num_central = str_cuadrado[inicio:fin]
            ri = int(num_central) / (10 ** longitud)
            
            tabla.append([i, semilla, str_cuadrado, len(str_cuadrado), num_central, f"{ri}"])
            numeros.append(ri)
            semilla = int(num_central)
        
        tabla_formateada = tabulate(tabla, 
                                  headers=["Iteración", "Semilla", "Cuadrado", "Longitud", "Central", "ri"],
                                  tablefmt="grid")
        
        return numeros, tabla_formateada
    
    def metodo_productos_medios(self, semilla1, semilla2, n):
        longitud = len(str(semilla1))
        longitud2 = len(str(semilla2))
        if longitud % 2 != 0:
            raise ValueError("La semilla debe tener longitud par")
        if longitud2 != longitud:
            raise ValueError("semilla 2 debe ser del mimo tamaño que la 1")
        
        numeros = []
        tabla = []
        
        for i in range(1, n + 1):
            producto = semilla1 * semilla2
            str_producto = str(producto).zfill(longitud * 2)
            inicio = (len(str_producto) - longitud) // 2
            fin = inicio + longitud
            num_central = str_producto[inicio:fin]
            ri = int(num_central) / (10 ** longitud)
            
            tabla.append([i, semilla1, semilla2, str_producto, len(str_producto), num_central, f"{ri}"])
            numeros.append(ri)
            semilla1 = semilla2
            semilla2 = int(num_central)
        
        tabla_formateada = tabulate(tabla,
                                  headers=["Iteración", "Semilla1", "Semilla2", "Producto", "Longitud", "Central", "ri"],
                                  tablefmt="grid")
        
        return numeros, tabla_formateada
    
    def metodo_constante_multiplicativa(self, semilla, multiplier, n):
        longitud = len(str(semilla))
        longitud2 = len(str(multiplier))
        if longitud % 2 != 0:
            raise ValueError("La semilla debe tener longitud par")
        if longitud2 != longitud:
            raise ValueError("multiplicador debe ser del mimo tamaño que la semilla")
        
        
        numeros = []
        tabla = []
        
        for i in range(1, n + 1):
            producto = semilla * multiplier
            str_producto = str(producto).zfill(longitud * 2)
            inicio = (len(str_producto) - longitud) // 2
            fin = inicio + longitud
            num_central = str_producto[inicio:fin]
            ri = int(num_central) / (10 ** longitud)
            
            tabla.append([i, semilla, multiplier, str_producto, len(str_producto), num_central, f"{ri}"])
            numeros.append(ri)
            semilla = int(num_central)
        
        tabla_formateada = tabulate(tabla,
                                  headers=["Iteración", "Semilla", "Multiplicador", "Producto", "Longitud", "Central", "ri"],
                                  tablefmt="grid")
        
        return numeros, tabla_formateada
    
    def metodo_lineal(self, semilla, a, c, m, n):
        try:
            semilla = int(semilla)
            a = int(a)
            c = int(c)  # <--- Conversión explícita a entero
            m = int(m)
        except ValueError:
            raise ValueError("Todos los parámetros (semilla, a, c, m) deben ser enteros")
        str_semilla = str(semilla)
        str_a = str(a)
        lon = len(str(c))
    
        longitud_semilla = len(str_semilla)
    
    # Verificar que la semilla tenga longitud par (si es requerido)
        if longitud_semilla % 2 != 0:
            raise ValueError("La semilla debe tener longitud par")
    
    # Verificar que 'a' y 'c' tengan la misma longitud que la semilla
        if len(str_a) != longitud_semilla:
            raise ValueError("El multiplicador (a) debe tener la misma longitud que la semilla")
        if lon != longitud_semilla:
            raise ValueError("El incremento (c) debe tener la misma longitud que la semilla  -")


        numeros = []
        tabla = []
        
        for i in range(1, n + 1):
            siguiente = (a * semilla + c) % m
            ri = siguiente / (m - 1)
            
            tabla.append([i, semilla, a, c, m, siguiente, f"{ri}"])
            numeros.append(ri)
            semilla = siguiente
        
        tabla_formateada = tabulate(tabla,
                                  headers=["Iteración", "Semilla", "a", "c", "m", "Siguiente", "ri"],
                                  tablefmt="grid")
        
        return numeros, tabla_formateada
    
    # Pruebas estadísticas
    def prueba_chi_cuadrada(self, datos, confianza):
        n = len(datos)
        intervalos = int(round(sqrt(n)))
        amplitud = 1 / intervalos
        limites = np.linspace(0, 1, intervalos + 1)
        
        observados, _ = np.histogram(datos, bins=limites)
        esperados = np.full(intervalos, n / intervalos)
        
        chi_calc = np.sum((observados - esperados) ** 2 / esperados)
        alpha = 1 - confianza
        gl = intervalos - 1
        critico = chi2.ppf(1 - alpha, gl)
        decision = "Aceptar" if chi_calc < critico else "Rechazar"
        
        tabla = []
        for i in range(intervalos):
            tabla.append([
                i + 1,
                f"{limites[i]:.6f}",
                f"{limites[i + 1]:.6f}",
                observados[i],
                f"{esperados[i]:.6f}",
                f"{((observados[i] - esperados[i]) ** 2 / esperados[i]):.6f}"
            ])
        
        tabla.append(["Total", "", "", np.sum(observados), "", f"{chi_calc:.6f}"])
        
        tabla_formateada = tabulate(tabla,
                                  headers=["Intervalo", "Lím. Inf.", "Lím. Sup.", "Observado", "Esperado", "X²"],
                                  tablefmt="grid")
        
        resultados = (
            f"Valor crítico: {critico:.6f}\n"
            f"Estadístico Chi²: {chi_calc:.6f}\n"
            f"Decisión: {decision} hipótesis\n"
            f"Grados libertad: {gl}\n"
            f"Amplitud: {amplitud:.6f}\n"
            f"Alpha: {alpha:.6f}"
        )
        
        return tabla_formateada, resultados
    
    def prueba_kolmogorov(self, datos, confianza):
        datos = sorted(datos)
        n = len(datos)
        
        Dn = 0
        tabla = []
        for i, val in enumerate(datos):
            emp = (i + 1) / n
            teo = val
            dif = abs(emp - teo)
            Dn = max(Dn, dif)
            
            tabla.append([
                i + 1,
                f"{val:.6f}",
                f"{emp:.6f}",
                f"{teo:.6f}",
                f"{dif:.6f}"
            ])
        
        alpha = 1 - confianza
        critico = kstwobign.ppf(1 - alpha) / sqrt(n)
        decision = "Aceptar" if Dn <= critico else "Rechazar"
        
        tabla_formateada = tabulate(tabla,
                                  headers=["Iteración", "Valor", "Empírica", "Teórica", "Diferencia"],
                                  tablefmt="grid")
        
        resultados = (
            f"Estadístico Dn: {Dn:.6f}\n"
            f"Valor crítico: {critico:.6f}\n"
            f"Decisión: {decision} hipótesis\n"
            f"Muestra: {n}\n"
            f"Alpha: {alpha:.6f}"
        )
        
        return tabla_formateada, resultados
    
    def prueba_arriba_abajo(self, datos, confianza):
        corridas = []
        signo_anterior = None
        contador = 0
        
        for i in range(1, len(datos)):
            if datos[i] > datos[i - 1]:
                signo = "+"
            else:
                signo = "-"
            
            if signo != signo_anterior:
                contador += 1
                corridas.append([i, f"{datos[i - 1]:.6f}", f"{datos[i]:.6f}", signo])
            
            signo_anterior = signo
        
        n = len(datos)
        esperado = (2 * n - 1) / 3
        varianza = (16 * n - 29) / 90
        estadistico = abs((contador - esperado) / sqrt(varianza))
        alpha = 1 - confianza
        critico = norm.ppf(1 - alpha / 2)
        decision = "Aceptar" if estadistico < critico else "Rechazar"
        
        tabla_corridas = tabulate(corridas,
                                headers=["Posición", "Anterior", "Actual", "Signo"],
                                tablefmt="grid")
        
        tabla_resultados = tabulate([[contador, n, f"{esperado:.6f}", f"{varianza:.6f}", 
                                   f"{estadistico:.6f}", f"{critico:.6f}"]],
                                  headers=["Corridas", "n", "Esperado", "Varianza", "Estadístico", "Crítico"],
                                  tablefmt="grid")
        
        resultados = (
            f"Decisión: {decision} hipótesis\n"
            f"Confianza: {confianza:.2%}\n"
            f"Estadístico: {estadistico:.6f}\n"
            f"Valor crítico: {critico:.6f}\n"
            f"Alpha/2: {alpha/2:.6f}"
        )
        
        return f"{tabla_corridas}\n\n{tabla_resultados}", resultados
    
    def prueba_arriba_debajo_media(self, datos, confianza):
        media = np.mean(datos)
        direcciones = [1 if num > media else 0 for num in datos]
    
        # Detección de rachas y cambios
        cambios = []
        contador = 1  # Siempre hay al menos 1 racha
    
        for i in range(1, len(direcciones)):
            if direcciones[i] != direcciones[i-1]:
                contador += 1
                cambios.append("→")  # Marcador de cambio
            else:
                cambios.append("")
    
        # Preparamos datos para tabla (similar a tu versión original)
        tabla_datos = []
        for i in range(len(direcciones)):
            fila = [
                f"{datos[i]:.4f}",
                direcciones[i],
                cambios[i-1] if i > 0 else ""  # El primer elemento no tiene cambio previo
            ]
            tabla_datos.append(fila)
    
        # Tabla de direcciones y rachas (como en tu original)
        tabla_dir_rachas = tabulate(
            tabla_datos,
            headers=["Dato", "Dirección (1=↑, 0=↓)", "Cambio"],
            tablefmt="grid",
            stralign="center"
        )
    
        # Cálculos estadísticos (manteniendo tu lógica exacta)
        n0 = direcciones.count(0)
        n1 = direcciones.count(1)
        n = len(datos)
    
        media_esperada = ((2 * n0 * n1) / n) + 0.5
        varianza = (2 * n0 * n1 * (2 * n0 * n1 - n)) / (n**2 * (n - 1))
        desviacion = sqrt(varianza)
        estadistico = abs((contador - media_esperada) / desviacion)
        alpha = 1 - confianza
        critico = norm.ppf(1 - alpha / 2)
        decision = "Aceptar" if estadistico < critico else "Rechazar"
    
        # Resultados en formato string (como en tu versión original)
        resultados = (
            f"Media: {media:.6f}\n"
            f"n0 (abajo media): {n0}\n"
            f"n1 (arriba media): {n1}\n"
            f"Número de corridas: {contador}\n"
            f"Media esperada: {media_esperada:.6f}\n"
            f"Varianza: {varianza:.6f}\n"
            f"Estadístico Z: {estadistico:.6f}\n"
            f"Valor crítico: {critico:.6f}\n"
            f"Decisión: {decision}\n"
            f"Confianza: {confianza:.2%}\n"
            f"Alpha/2: {alpha/2:.6f}"
        )
    
        return tabla_dir_rachas, resultados
    
    def prueba_poker(self, datos, confianza, digitos=5):
        if digitos not in [3, 4, 5]:
            raise ValueError("Dígitos debe ser 3, 4 o 5")

        # Convertir números a cadenas con los dígitos especificados
        str_nums = []
        for num in datos:
        # Primero convertir a float y luego a entero para manejar strings y floats
            num_entero = int(float(num) * (10 ** digitos))  # Multiplicar por 10^digitos para mover decimales
            num_str = str(abs(num_entero)).zfill(digitos)[-digitos:]  # Tomar los últimos 'digitos' dígitos
            str_nums.append(num_str)

        if digitos == 3:
            todos = par = tercia = 0
        elif digitos == 4:
            todos = par = par2 = tercia = poker = 0
        else:  # 5 dígitos
            todos = par = par2 = tercia = poker = full = quinti = 0

        for num in str_nums:
            conteo = {}
            for d in num:
                conteo[d] = conteo.get(d, 0) + 1
        
            valores = list(conteo.values())
        
            if digitos == 3:
                if 3 in valores:
                    tercia += 1
                elif 2 in valores:
                    par += 1
                else:
                    todos += 1
            elif digitos == 4:
                if 4 in valores:
                    poker += 1
                elif 3 in valores:
                    tercia += 1
                elif valores.count(2) == 2:
                    par2 += 1
                elif 2 in valores:
                    par += 1
                else:
                    todos += 1
            else:  # 5 dígitos
                if 5 in valores:
                    quinti += 1
                elif 4 in valores:
                    poker += 1
                elif 3 in valores and 2 in valores:
                    full += 1
                elif 3 in valores:
                    tercia += 1
                elif valores.count(2) == 2:
                    par2 += 1
                elif 2 in valores:
                    par += 1
                else:
                    todos += 1

        if digitos == 3:
            categorias = ["TD", "Par", "Tercia"]
            freobs = [todos, par, tercia]
            freesp = [0.72*len(datos), 0.27*len(datos), 0.01*len(datos)]
        elif digitos == 4:
            categorias = ["TD", "Par", "2 par", "Tercia", "Póker"]
            freobs = [todos, par, par2, tercia, poker]
            freesp = [0.504*len(datos), 0.432*len(datos), 0.027*len(datos), 0.036*len(datos), 0.001*len(datos)]
        else:  # 5 dígitos
            categorias = ["TD", "Par", "2 par", "Tercia", "Póker", "Full", "Quintilla"]
            freobs = [todos, par, par2, tercia, poker, full, quinti]
            freesp = [0.3024*len(datos), 0.504*len(datos), 0.108*len(datos), 0.072*len(datos), 
                     0.0045*len(datos), 0.009*len(datos), 0.0001*len(datos)]

        # Calcular chi-cuadrado
        chi_calc = 0
        tabla = []
        for i in range(len(categorias)):
            obs = freobs[i]
            esp = freesp[i]
            contrib = (obs - esp) ** 2 / esp if esp > 0 else 0
            chi_calc += contrib
            tabla.append([categorias[i], obs, f"{esp:.4f}", f"{contrib:.4f}"])

        alpha = 1 - confianza
        gl = len(categorias) - 1
        critico = chi2.ppf(1 - alpha, gl)
        decision = "Aceptar" if chi_calc < critico else "Rechazar"

        tabla_formateada = tabulate(tabla,
                                headers=["Categoría", "Observado", "Esperado", "Contribución"],
                                tablefmt="grid")

        resultados = (
            f"Estadístico Chi²: {chi_calc:.6f}\n"
            f"Valor crítico: {critico:.6f}\n"
            f"Decisión: {decision} hipótesis\n"
            f"Grados libertad: {gl}\n"
            f"Alpha: {alpha:.6f}\n"
            f"Dígitos usados: {digitos}"
        )

        return tabla_formateada, resultados
    
    def prueba_huecos(self, datos, alpha, beta, confianza):
        # 1. Convertir a binarios (1 si está en [α, β], 0 si no)
        uno0s = [1 if alpha <= num <= beta else 0 for num in datos]
        valores_en_intervalo = sum(uno0s)  # Total de números en el intervalo [α, β]

        # Si no hay ningún valor en el intervalo, la prueba no es aplicable
        if valores_en_intervalo == 0:
            mensaje = f"No hay valores en el intervalo [α={alpha:.4f}, β={beta:.4f}]"
            return mensaje, "Prueba no aplicable (no hay valores en el intervalo)"

        # Si solo hay un '1', no se pueden formar huecos
        if valores_en_intervalo == 1:
            resultados = (
                f"Solo hay un valor en el intervalo [α={alpha:.4f}, β={beta:.4f}].\n"
                "No se pueden formar huecos (se necesitan al menos dos valores)."
            )
            tabla_conv = [[i + 1, f"{num:.6f}", uno0s[i]] for i, num in enumerate(datos)]
            tabla_conv_formateada = tabulate(
                tabla_conv,
                headers=["Índice", "Número", "Binario (1 si está en [α,β])"],
                tablefmt="grid"
            )
            return tabla_conv_formateada, resultados

        # 2. Contar huecos (solo si hay al menos dos '1's)
        huecos_cont = [0, 0, 0, 0, 0, 0]  # Huecos de tamaño 0, 1, 2, 3, 4, >=5
        hueco_actual = 0
        contando = False

        for bit in uno0s:
            if bit == 1:
                if contando:  # Si ya estábamos en un hueco, lo registramos
                    if hueco_actual < 5:
                        huecos_cont[hueco_actual] += 1
                    else:
                        huecos_cont[5] += 1
                    hueco_actual = 0  # Reiniciamos el contador
                contando = True  # Empezamos a buscar un nuevo hueco
            else:
                if contando:
                    hueco_actual += 1  # Incrementamos el tamaño del hueco actual

        # 3. Calcular frecuencias esperadas y Chi²
        total_huecos = valores_en_intervalo - 1  # N° de huecos = n° de '1's - 1
        tamhueco = ["0", "1", "2", "3", "4", ">=5"]
        sumx2 = 0
        tabla = []

        for i in range(len(tamhueco)):
            if i < 5:
                # Probabilidad para huecos de tamaño 0-4
                prob = (beta - alpha) * ((1 - (beta - alpha)) ** i)
            else:
                # Probabilidad para huecos >=5
                prob = (1 - (beta - alpha)) ** 5
            
            frec_esperada = total_huecos * prob
            chi_cuadrado = ((huecos_cont[i] - frec_esperada) ** 2) / frec_esperada if frec_esperada != 0 else 0
            sumx2 += chi_cuadrado
            tabla.append([tamhueco[i], huecos_cont[i], f"{frec_esperada:.4f}", f"{chi_cuadrado:.4f}"])

        # 4. Realizar la prueba Chi²
        alfa = 1 - confianza
        gl = 5  # Grados de libertad (6 categorías - 1)
        valor_critico = chi2.ppf(1 - alfa, gl)
        decision = "Se acepta la hipótesis de aleatoriedad" if sumx2 < valor_critico else "Se rechaza la hipótesis"

        # 5. Generar tablas de resultados
        tabla_conv = [[i + 1, f"{num:.6f}", uno0s[i]] for i, num in enumerate(datos)]
        tabla_conv_formateada = tabulate(
            tabla_conv,
            headers=["Índice", "Número", "Binario (1 si está en [α,β])"],
            tablefmt="grid"
        )

        tabla_res_formateada = tabulate(
            tabla,
            headers=["Tamaño Hueco", "Frec Observada", "Frec Esperada", "Chi²"],
            tablefmt="grid"
        )

        # 6. Resultados finales
        resultados = (
            f"RESULTADOS DE LA PRUEBA DE HUECOS:\n"
            f"• Intervalo analizado: [α={alpha:.4f}, β={beta:.4f}]\n"
            f"• Total de valores en el intervalo: {valores_en_intervalo}\n"
            f"• Suma Chi²: {sumx2:.4f}\n"
            f"• Valor crítico (α={alfa:.3f}): {valor_critico:.4f}\n"
            f"• Decisión: {decision}\n"
        )

        return f"{tabla_conv_formateada}\n\n{tabla_res_formateada}", resultados

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneradorNumerosApp(root)
    root.mainloop()