import sqlite3
import tkinter as tk
from tkinter import filedialog
import csv
import re
from collections import defaultdict

# Conexión y creación de la base de datos y tablas
def crear_bd():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Archivo (
            id INTEGER PRIMARY KEY,
            nombre TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Linea (
            id INTEGER PRIMARY KEY,
            archivo_id INTEGER,
            inicio TEXT,
            fin TEXT,
            texto TEXT,
            FOREIGN KEY (archivo_id) REFERENCES Archivo(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Palabra (
            id INTEGER PRIMARY KEY,
            texto TEXT UNIQUE,
            isKey BOOLEAN DEFAULT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LineaPalabra (
            id INTEGER PRIMARY KEY,
            linea_id INTEGER,
            palabra_id INTEGER,
            vecesQueAparece INTEGER,
            FOREIGN KEY (linea_id) REFERENCES Linea(id),
            FOREIGN KEY (palabra_id) REFERENCES Palabra(id)
        )
    ''')

    conn.commit()
    return conn

# Función para normalizar palabras
def normalizar_palabra(palabra):
    palabra = palabra.lower()
    palabra = re.sub(r'\W+', '', palabra)  # Eliminar símbolos
    return palabra

# Selección de archivos y procesamiento
def procesar_archivos(conn):
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV/TSV files", "*.csv *.tsv")])

    cursor = conn.cursor()

    for file_path in file_paths:
        file_name = file_path.split('/')[-1]
        cursor.execute("INSERT OR IGNORE INTO Archivo (nombre) VALUES (?)", (file_name,))
        archivo_id = cursor.lastrowid if cursor.lastrowid != 0 else cursor.execute("SELECT id FROM Archivo WHERE nombre = ?", (file_name,)).fetchone()[0]

        with open(file_path, newline='', encoding='utf-8') as f:
            delimiter = '\t' if file_path.endswith('.tsv') else ','
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                inicio, fin, texto = row[0], row[1], row[2]
                cursor.execute("INSERT INTO Linea (archivo_id, inicio, fin, texto) VALUES (?, ?, ?, ?)", (archivo_id, inicio, fin, texto))
                linea_id = cursor.lastrowid

                # Contar palabras y actualizar en la tabla de palabras y el crossreference
                palabras_contadas = defaultdict(int)
                for palabra in texto.split():
                    palabra_normalizada = normalizar_palabra(palabra)
                    if palabra_normalizada:
                        palabras_contadas[palabra_normalizada] += 1

                for palabra, veces in palabras_contadas.items():
                    cursor.execute("INSERT OR IGNORE INTO Palabra (texto) VALUES (?)", (palabra,))
                    palabra_id = cursor.lastrowid if cursor.lastrowid != 0 else cursor.execute("SELECT id FROM Palabra WHERE texto = ?", (palabra,)).fetchone()[0]
                    cursor.execute("INSERT INTO LineaPalabra (linea_id, palabra_id, vecesQueAparece) VALUES (?, ?, ?)", (linea_id, palabra_id, veces))

    conn.commit()
    print("Archivos procesados y datos insertados en la base de datos.")

# Ejecución del programa
conn = crear_bd()
procesar_archivos(conn)
conn.close()

