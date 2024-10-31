WITH FrecuenciaPorArchivo AS (
    SELECT
        p.id AS palabra_id,
        p.palabra,
        l.archivo_id,
        SUM(c.times) AS total_apariciones
    FROM CrossReference c
    JOIN Palabra p ON c.palabra_id = p.id
    JOIN Linea l ON c.linea_id = l.id
    GROUP BY p.palabra, l.archivo_id
),
RangoApariciones AS (
    SELECT
        palabra_id,
        MAX(total_apariciones) AS max_apariciones,
        MIN(total_apariciones) AS min_apariciones,
        (MAX(total_apariciones) - MIN(total_apariciones)) AS rango,
        COUNT(DISTINCT archivo_id) AS archivos_presencia
    FROM FrecuenciaPorArchivo
    GROUP BY palabra_id
)
UPDATE Palabra
SET isKey = CASE
    WHEN id IN (
        SELECT palabra_id
        FROM RangoApariciones
        WHERE rango > 5  -- Permitir un rango más amplio
        AND archivos_presencia BETWEEN 3 AND 25  -- Aumentar la cantidad de archivos permitidos
    ) THEN 1  -- Marca como clave
    ELSE 0  -- Marca como no clave
END
WHERE id IN (
    SELECT palabra_id FROM RangoApariciones
);
