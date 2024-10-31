import sqlite3

def mostrar_palabras_clave():
    # Conectar a la base de datos
    conn = sqlite3.connect('archivos.db')
    cursor = conn.cursor()

    # Obtener las palabras clave y sus conteos por archivo
    cursor.execute('''
        SELECT a.nombre AS archivo, p.palabra, SUM(cr.times) AS total
        FROM CrossReference cr
        JOIN Palabra p ON cr.palabra_id = p.id
        JOIN Linea l ON cr.linea_id = l.id
        JOIN Archivo a ON l.archivo_id = a.id
        WHERE p.isKey = 1
        GROUP BY a.nombre, p.palabra
        HAVING total >= 3  -- Ignorar palabras que aparecen menos de 3 veces
        ORDER BY a.nombre, total DESC
    ''')

    # Procesar los resultados
    resultados = cursor.fetchall()

    # Organizar los resultados por archivo
    archivos_palabras = {}
    for archivo, palabra, total in resultados:
        if archivo not in archivos_palabras:
            archivos_palabras[archivo] = []
        archivos_palabras[archivo].append((total, palabra))

    # Mostrar resultados
    for archivo, palabras in archivos_palabras.items():
        print(f"\n{archivo}")
        for total, palabra in sorted(palabras, key=lambda x: x[0], reverse=True):
            print(f"  {total:03d} - {palabra}")

    # Cerrar la conexión
    conn.close()

# Ejecutar la función
mostrar_palabras_clave()
