# Limpieza de datos: Cafe Sales (Dirty Data for Cleaning Training)

**Actividad 4 - Práctica de limpieza de datos**
Materia: Análisis y Visualización de la Información (26B)

Isaac Arturo Camarillo Vega - código 220083026

## Objetivo

Aplicar técnicas de limpieza y transformación de datos con Python sobre una base diseñada para contener problemas de calidad, siguiendo un procedimiento documentado y justificado paso a paso.

## Dataset

[Cafe Sales - Dirty Data for Cleaning Training](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training) (Kaggle, autor: Ahmed Mohamed). 10,000 transacciones de una cafetería con 8 columnas: `Transaction ID`, `Item`, `Quantity`, `Price Per Unit`, `Total Spent`, `Payment Method`, `Location` y `Transaction Date`. El dataset se distribuye con valores faltantes, marcadores de error y tipos de dato inconsistentes.

## Contenido del repositorio

| Archivo | Descripción |
|---|---|
| `dirty_cafe_sales.csv` | Base original, sin modificar |
| `cafe_sales_cleaning.ipynb` | Notebook con la inspección, el análisis de problemas y la limpieza paso a paso, con salidas ya ejecutadas |
| `clean_cafe_sales.py` | Mismo procedimiento de limpieza en forma de script, para ejecutarlo por línea de comandos |
| `cafe_sales_clean.csv` | Base final, ya limpia (9,540 filas) |
| `README.md` | Este archivo |

## Procedimiento

1. **Carga e inspección inicial**: se cargó `dirty_cafe_sales.csv` con pandas y se revisaron tipos de dato, valores únicos por columna y conteo de nulos.
2. **Identificación de problemas**: se detectó que "ERROR" y "UNKNOWN" aparecen como texto en varias columnas (incluidas las numéricas), que las columnas numéricas y de fecha se leyeron como texto, y se verificó la ausencia de duplicados y la presencia de posibles valores atípicos mediante el rango intercuartílico (IQR).
3. **Limpieza y transformación**:
   - Se homologaron "ERROR" y "UNKNOWN" a `NaN` en todo el dataframe.
   - Se convirtieron `Quantity`, `Price Per Unit` y `Total Spent` a numérico, y `Transaction Date` a fecha, con coerción.
   - Se recuperaron los valores faltantes de `Quantity`, `Price Per Unit` y `Total Spent` usando la relación `Total Spent = Quantity × Price Per Unit`, verificada sin excepciones en las 8,544 filas donde las tres columnas eran válidas.
   - Se recuperó `Item` quando el precio identifica un único producto (1.0, 1.5, 2.0 o 5.0); cuando el precio es ambiguo (3.0 o 4.0) o también falta, se etiquetó como `"Unknown"`.
   - `Payment Method` y `Location` faltantes se etiquetaron como `"Unknown"` en vez de eliminar las filas.
   - Se eliminaron las filas con `Transaction Date` inválida o faltante (4.6% del total), por no poder reconstruirse a partir de otras columnas.
   - Se verificaron duplicados exactos y por `Transaction ID`: no se encontró ninguno.
   - Los "atípicos" que señaló el IQR en `Total Spent` (259 filas) se revisaron uno por uno antes de decidir: todos corresponden a `Quantity = 5 × Price Per Unit = 5.0 = 25`, la combinación más cara válida del catálogo, así que no se modificaron ni se eliminaron.
4. **Exportación**: la base limpia se guardó como `cafe_sales_clean.csv` (9,540 de las 10,000 filas originales; 26 filas conservan algún dato numérico incompleto porque no había información suficiente para recuperarlo).

## Tabla resumen de problemas y decisiones

| Problema encontrado | Registros afectados | Acción realizada | Justificación |
|---|---|---|---|
| Valores no permitidos ("ERROR" / "UNKNOWN") en cualquier columna | 2,845 filas | Homologados a `NaN` | No son categorías reales, son marcadores de dato inválido |
| Tipos de datos incorrectos (`Quantity`, `Price Per Unit`, `Total Spent`, `Transaction Date` como texto) | 10,000 filas | Conversión con `pd.to_numeric()` / `pd.to_datetime()` (con coerción) | Sin el tipo correcto no se pueden hacer operaciones aritméticas ni de fecha |
| `Quantity` / `Price Per Unit` / `Total Spent` faltantes | 1,456 filas (1,430 recuperadas por completo) | Recuperación con `Total = Quantity × Precio`, usando el precio de catálogo cuando hacía falta | La fórmula se cumplió sin excepciones en las 8,544 filas completas: es un cálculo exacto, no una estimación |
| `Item` faltante | 969 filas | 489 recuperadas por precio único; 480 marcadas `"Unknown"` | El precio no identifica un producto único cuando vale 3.0 o 4.0; adivinar inventaría información |
| `Payment Method` faltante | 3,178 filas | Sustituido por `"Unknown"` | Eliminar esas filas descartaría ~32% del dataset |
| `Location` faltante | 3,961 filas | Sustituido por `"Unknown"` | Eliminar esas filas descartaría ~40% del dataset |
| Duplicados (filas exactas y `Transaction ID`) | 0 filas | Verificado, sin acción | El dataset no contenía duplicados |
| Valores atípicos en `Total Spent` (criterio IQR) | 259 filas señaladas | No se modificaron ni eliminaron | Corresponden a ventas válidas (`5 × 5 = 25`), no a errores de captura |
| `Transaction Date` inválida o faltante | 460 filas (4.6%) | Eliminadas del dataset final | No se puede reconstruir a partir de otras columnas |

**Filas iniciales:** 10,000 · **Filas en la base limpia:** 9,540

## Cómo ejecutarlo

```bash
pip install pandas numpy matplotlib
python clean_cafe_sales.py
# o, para ver el análisis completo paso a paso:
jupyter notebook cafe_sales_cleaning.ipynb
```

## Declaración de IA generativa

Durante la preparación de este trabajo, el autor utilizó Claude (Anthropic) para explorar el dataset, estructurar el procedimiento de limpieza y redactar este README. Después de utilizar esta herramienta/servicio, el autor revisó y editó el contenido según fue necesario y asume la responsabilidad total por el contenido de este trabajo.
