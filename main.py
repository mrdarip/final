import tkinter as tk
from tkinter import filedialog
import pandas as pd
import sqlite3
import re
from collections import Counter

# Crear la base de datos y definir tablas
def create_database():
    conn = sqlite3.connect('archivos.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Archivo (
                        id INTEGER PRIMARY KEY,
                        nombre TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Linea (
                        id INTEGER PRIMARY KEY,
                        archivo_id INTEGER,
                        texto TEXT,
                        inicio INTEGER,
                        fin INTEGER,
                        FOREIGN KEY (archivo_id) REFERENCES Archivo(id))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS Palabra (
                        id INTEGER PRIMARY KEY,
                        palabra TEXT UNIQUE,
                        isKey BOOLEAN DEFAULT NULL)''')  # Nueva columna isKey
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS CrossReference (
                        linea_id INTEGER,
                        palabra_id INTEGER,
                        times INTEGER,
                        FOREIGN KEY (linea_id) REFERENCES Linea(id),
                        FOREIGN KEY (palabra_id) REFERENCES Palabra(id),
                        PRIMARY KEY (linea_id, palabra_id))''')
    
    conn.commit()
    conn.close()

# Normalizar palabras
def normalizar_palabra(palabra):
    # Convertir a minúsculas y eliminar caracteres no alfanuméricos
    palabra = palabra.lower()
    palabra = re.sub(r'[^a-zA-Z0-9áéíóúüñ]', '', palabra)  # Conservar caracteres alfanuméricos y letras acentuadas
    return palabra

# Seleccionar archivos y extraer datos
def seleccionar_archivos():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV and TSV files", "*.csv *.tsv")])
    
    if not file_paths:
        print("No se seleccionaron archivos.")
        return

    # Crear la base de datos
    create_database()
    
    conn = sqlite3.connect('archivos.db')
    cursor = conn.cursor()
    
    for file_path in file_paths:
        file_name = file_path.split('/')[-1]
        
        # Insertar el archivo en la base de datos
        cursor.execute("INSERT INTO Archivo (nombre) VALUES (?)", (file_name,))
        archivo_id = cursor.lastrowid
        
        # Leer archivo
        delimiter = ',' if file_name.endswith('.csv') else '\t'
        df = pd.read_csv(file_path, delimiter=delimiter)
        
        # Verificar si existen las columnas necesarias
        if df.shape[1] < 3:
            print(f"El archivo {file_name} no tiene suficientes columnas.")
            continue
        
        # Leer y guardar datos en la base de datos
        # Ajuste en la sección de lectura y procesamiento de cada fila
        for index, row in df.iterrows():
            # Cambiar el acceso directo a `row[]` por `row.iloc[]`
            texto, inicio, fin = row.iloc[2], row.iloc[0], row.iloc[1]
            
            # Insertar la línea en la base de datos con inicio y fin
            cursor.execute("INSERT INTO Linea (archivo_id, texto, inicio, fin) VALUES (?, ?, ?, ?)", 
                        (archivo_id, texto, inicio, fin))
            linea_id = cursor.lastrowid
                
            # Normalizar y contar la frecuencia de cada palabra en la línea
            palabras = texto.split()
            palabras_normalizadas = [normalizar_palabra(p) for p in palabras if normalizar_palabra(p)]
            contador_palabras = Counter(palabras_normalizadas)
                
            for palabra, times in contador_palabras.items():
                # Insertar la palabra en la tabla de Palabra si no existe y obtener el id de la palabra
                cursor.execute("INSERT OR IGNORE INTO Palabra (palabra) VALUES (?)", (palabra,))
                    
                # Obtener el id de la palabra, ya sea la recién insertada o la que ya existía
                cursor.execute("SELECT id FROM Palabra WHERE palabra = ?", (palabra,))
                palabra_id = cursor.fetchone()[0]
                    
                # Insertar la referencia cruzada en la tabla CrossReference con la frecuencia
                cursor.execute("INSERT INTO CrossReference (linea_id, palabra_id, times) VALUES (?, ?, ?)", (linea_id, palabra_id, times))

    conn.commit()
    conn.close()
    print("Datos guardados en la base de datos 'archivos.db'.")

# Ejecutar la selección de archivos
seleccionar_archivos()
