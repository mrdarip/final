import sqlite3

def actualizar_palabras_clave():
    # Conectar a la base de datos
    conn = sqlite3.connect('archivos.db')
    cursor = conn.cursor()

    # Obtener las palabras con isKey = NULL y su conteo
    cursor.execute('''
        SELECT p.id, p.palabra, SUM(cr.times) AS total
        FROM Palabra p
        JOIN CrossReference cr ON p.id = cr.palabra_id
        WHERE p.isKey IS NULL
        GROUP BY p.id, p.palabra
        ORDER BY total DESC
    ''')
    palabras = cursor.fetchall()

    if not palabras:
        print("No hay palabras con isKey = NULL.")
        conn.close()
        return

    total_palabras = len(palabras)

    # Mostrar palabras y permitir al usuario actualizar su estado
    for index, (palabra_id, palabra, total) in enumerate(palabras):
        print(f"\nPalabra: {palabra} (Aparece: {total} veces, Quedan: {total_palabras - index})")
        respuesta = input("¿Es clave? (y/n o dejar en blanco para NULL): ").strip().lower()

        if respuesta == 'y':
            cursor.execute("UPDATE Palabra SET isKey = 1 WHERE id = ?", (palabra_id,))
            print(f"Se ha marcado '{palabra}' como clave.")
        elif respuesta == 'n':
            cursor.execute("UPDATE Palabra SET isKey = 0 WHERE id = ?", (palabra_id,))
            print(f"Se ha marcado '{palabra}' como no clave.")
        elif respuesta == '':
            print(f"No se ha cambiado el estado de '{palabra}'.")
        else:
            print("Respuesta no válida. Se ignora la entrada.")
        
        # Hacer commit para guardar cambios inmediatamente
        conn.commit()

    # Cerrar la conexión
    conn.close()
    print("Actualización completada.")

# Ejecutar la función
actualizar_palabras_clave()
