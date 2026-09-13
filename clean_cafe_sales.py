"""
Limpieza de datos: Cafe Sales - Dirty Data for Cleaning Training
Actividad 4 - Practica de limpieza de datos
Isaac Arturo Camarillo Vega

Fuente del dataset:
https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training

Este script carga el archivo dirty_cafe_sales.csv, inspecciona los
problemas de calidad, aplica las tecnicas de limpieza justificadas en el
README y exporta cafe_sales_clean.csv. Tambien imprime, en cada paso, el
numero de registros afectados para poder construir la tabla resumen.
"""

import numpy as np
import pandas as pd

RAW_PATH = "dirty_cafe_sales.csv"
CLEAN_PATH = "cafe_sales_clean.csv"

# Precio fijo por producto, verificado en el propio dataset: para cada
# Item que aparece con un Price Per Unit valido, ese precio es siempre
# el mismo (nunique == 1 en todos los casos). Cake y Juice comparten
# precio (3.0), y Sandwich y Smoothie comparten precio (4.0), por lo que
# el precio NO identifica de forma unica al producto en esos dos casos.
CATALOG_PRICE = {
    "Cookie": 1.0,
    "Tea": 1.5,
    "Coffee": 2.0,
    "Cake": 3.0,
    "Juice": 3.0,
    "Sandwich": 4.0,
    "Smoothie": 4.0,
    "Salad": 5.0,
}
UNIQUE_PRICE_TO_ITEM = {1.0: "Cookie", 1.5: "Tea", 2.0: "Coffee", 5.0: "Salad"}


def load_raw(path=RAW_PATH):
    return pd.read_csv(path)


def report(label, df):
    print(f"\n--- {label} ---")
    print("filas:", len(df))
    print(df.isna().sum())


def clean(df_raw):
    df = df_raw.copy()
    n_total = len(df)

    # 1) Valores no permitidos: "ERROR" / "UNKNOWN" no son categorias
    #    reales, son marcadores de dato invalido. Se homologan a NaN en
    #    todo el DataFrame para poder tratarlos con las herramientas
    #    estandar de pandas para datos faltantes.
    placeholder_mask = df.isin(["ERROR", "UNKNOWN"])
    rows_with_placeholder = placeholder_mask.any(axis=1).sum()
    df = df.replace(["ERROR", "UNKNOWN"], np.nan)
    print(f"[1] Filas con 'ERROR'/'UNKNOWN' homologadas a NaN: {rows_with_placeholder}")

    # 2) Tipos de datos incorrectos: las columnas numericas y de fecha se
    #    leyeron como texto porque contenian los marcadores del paso 1.
    #    Se convierten con coercion (los valores que no se puedan
    #    convertir quedan como NaN, ya sin perder mas informacion de la
    #    que ya se perdio en el paso anterior).
    for col in ["Quantity", "Price Per Unit", "Total Spent"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], errors="coerce")
    print(f"[2] Columnas convertidas a tipo numerico/fecha: Quantity, Price Per Unit, "
          f"Total Spent, Transaction Date (afecta las {n_total} filas)")

    # 3) Verificacion de duplicados (no se asume que no existan).
    dup_rows = df.duplicated().sum()
    dup_ids = df["Transaction ID"].duplicated().sum()
    print(f"[3] Filas duplicadas exactas: {dup_rows} | Transaction ID duplicados: {dup_ids}")
    df = df.drop_duplicates()

    # 4) Verificacion de valores atipicos en Quantity, Price Per Unit y
    #    Total Spent mediante rango intercuartilico. Solo se actua si el
    #    IQR detecta valores fuera de rango.
    outlier_counts = {}
    for col in ["Quantity", "Price Per Unit", "Total Spent"]:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outlier_counts[col] = len(outliers)
    print(f"[4] Valores atipicos detectados por IQR: {outlier_counts}")

    # 5) Recuperacion determinista de Quantity / Price Per Unit / Total
    #    Spent usando la relacion Total = Quantity * Price Per Unit,
    #    verificada sin excepciones en las filas donde las tres columnas
    #    eran validas.
    core = ["Quantity", "Price Per Unit", "Total Spent"]
    all_known_mask = df[core].notna().all(axis=1)
    check = df.loc[all_known_mask, "Total Spent"] - (
        df.loc[all_known_mask, "Quantity"] * df.loc[all_known_mask, "Price Per Unit"]
    )
    print(f"[5] Filas con las 3 columnas numericas completas: {all_known_mask.sum()} | "
          f"discrepancias Total != Qty*Precio: {(check.abs() > 0.01).sum()}")

    # 5a) Si falta el precio pero se conoce el producto, se recupera del
    #     catalogo (precio fijo por producto, confirmado en el dataset).
    mask_price_missing_item_known = df["Price Per Unit"].isna() & df["Item"].notna()
    df.loc[mask_price_missing_item_known, "Price Per Unit"] = df.loc[
        mask_price_missing_item_known, "Item"
    ].map(CATALOG_PRICE)
    n_price_from_catalog = mask_price_missing_item_known.sum()

    # 5b) Con Quantity y Precio conocidos, se completa Total Spent.
    mask_total_missing = (
        df["Total Spent"].isna() & df["Quantity"].notna() & df["Price Per Unit"].notna()
    )
    df.loc[mask_total_missing, "Total Spent"] = (
        df.loc[mask_total_missing, "Quantity"] * df.loc[mask_total_missing, "Price Per Unit"]
    )
    n_total_recovered = mask_total_missing.sum()

    # 5c) Con Total y Precio conocidos, se completa Quantity.
    mask_qty_missing = (
        df["Quantity"].isna() & df["Total Spent"].notna() & df["Price Per Unit"].notna()
    )
    df.loc[mask_qty_missing, "Quantity"] = (
        df.loc[mask_qty_missing, "Total Spent"] / df.loc[mask_qty_missing, "Price Per Unit"]
    ).round()
    n_qty_recovered = mask_qty_missing.sum()

    # 5d) Con Total y Quantity conocidos, se completa Precio (por si no
    #     se pudo recuperar en 5a, p. ej. porque tambien faltaba Item).
    mask_price_missing_2 = (
        df["Price Per Unit"].isna() & df["Total Spent"].notna() & df["Quantity"].notna()
    )
    df.loc[mask_price_missing_2, "Price Per Unit"] = (
        df.loc[mask_price_missing_2, "Total Spent"] / df.loc[mask_price_missing_2, "Quantity"]
    )
    n_price_recovered_2 = mask_price_missing_2.sum()

    print(f"[5a] Price Per Unit recuperado desde catalogo (Item conocido): {n_price_from_catalog}")
    print(f"[5b] Total Spent recuperado via Quantity x Precio: {n_total_recovered}")
    print(f"[5c] Quantity recuperado via Total / Precio: {n_qty_recovered}")
    print(f"[5d] Price Per Unit recuperado via Total / Quantity: {n_price_recovered_2}")

    # 6) Item faltante: se recupera solo cuando el precio identifica de
    #    forma unica a un producto (1.0, 1.5, 2.0, 5.0). Cuando el precio
    #    es 3.0 o 4.0 (ambiguo entre dos productos) o tambien falta, se
    #    etiqueta como "Unknown" en vez de adivinar.
    item_missing_mask = df["Item"].isna()
    n_item_missing_before = item_missing_mask.sum()
    recoverable_price = df["Price Per Unit"].isin(UNIQUE_PRICE_TO_ITEM.keys())
    mask_item_recoverable = item_missing_mask & recoverable_price
    df.loc[mask_item_recoverable, "Item"] = df.loc[
        mask_item_recoverable, "Price Per Unit"
    ].map(UNIQUE_PRICE_TO_ITEM)
    n_item_recovered = mask_item_recoverable.sum()
    df["Item"] = df["Item"].fillna("Unknown")
    n_item_unknown = (df["Item"] == "Unknown").sum()
    print(f"[6] Item faltante originalmente: {n_item_missing_before} | "
          f"recuperado desde precio unico: {n_item_recovered} | "
          f"marcado como 'Unknown' (precio ambiguo o tambien faltante): {n_item_unknown}")

    # 7) Payment Method y Location: no son deducibles de otras columnas.
    #    Se conservan las filas y se etiquetan como "Unknown" en vez de
    #    eliminarlas (representan ~30-40% del total).
    n_payment_missing = df["Payment Method"].isna().sum()
    n_location_missing = df["Location"].isna().sum()
    df["Payment Method"] = df["Payment Method"].fillna("Unknown")
    df["Location"] = df["Location"].fillna("Unknown")
    print(f"[7] Payment Method marcado como 'Unknown': {n_payment_missing} | "
          f"Location marcado como 'Unknown': {n_location_missing}")

    # 8) Transaction Date invalida o faltante: no se puede reconstruir a
    #    partir de otras columnas. Representa una fraccion pequena del
    #    total, asi que esas filas se retiran del dataset final.
    n_date_invalid = df["Transaction Date"].isna().sum()
    df = df.dropna(subset=["Transaction Date"])
    print(f"[8] Filas eliminadas por Transaction Date invalida/faltante: {n_date_invalid}")

    # 9) Filas que, tras todo lo anterior, siguen sin poder completarse en
    #    Quantity, Price Per Unit o Total Spent (no habia suficiente
    #    informacion para aplicar la formula). Se conservan (no se borran
    #    de mas) pero se reportan para que quede documentado.
    still_incomplete = df[["Quantity", "Price Per Unit", "Total Spent"]].isna().any(axis=1).sum()
    print(f"[9] Filas que siguen con Quantity/Precio/Total incompleto tras la recuperacion: {still_incomplete}")

    # 10) Tipos finales
    df["Quantity"] = df["Quantity"].astype("Int64")
    df["Item"] = df["Item"].astype("category")
    df["Payment Method"] = df["Payment Method"].astype("category")
    df["Location"] = df["Location"].astype("category")

    print(f"\nFilas iniciales: {n_total} | Filas finales: {len(df)}")
    return df


if __name__ == "__main__":
    raw = load_raw()
    report("Datos crudos (antes de limpiar)", raw.replace(["ERROR", "UNKNOWN"], np.nan))
    cleaned = clean(raw)
    report("Datos limpios (final)", cleaned)
    cleaned.to_csv(CLEAN_PATH, index=False)
    print(f"\nArchivo limpio exportado a: {CLEAN_PATH}")
