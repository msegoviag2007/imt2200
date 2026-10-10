"""Lectura de las 16 tablas del proyecto (4 tipos x 4 años) desde Drive."""
import pandas as pd

from src.config import ANIOS, IDS_DRIVE, TABLAS, URL_DRIVE


def leer_csv(clave: str) -> pd.DataFrame:
    """Lee directo desde Google Drive un CSV como 'IP-2026'.

    Los CSV del MINEDUC usan ';' como separador y coma decimal. No se guarda
    ninguna copia local: pandas descarga el archivo a memoria y lo lee.
    """
    url = URL_DRIVE.format(IDS_DRIVE[clave])
    print(f'Leyendo {clave} desde Google Drive ...')
    return pd.read_csv(url, sep=';', decimal=',', low_memory=False)


def cargar_tablas(anios: list[int] = ANIOS
                  ) -> dict[str, dict[int, pd.DataFrame]]:
    """Carga las tablas como {'IP': {2026: df, ...}, 'SD': {...}, ...}."""
    tablas = {}
    for sigla in TABLAS:
        tablas[sigla] = {}
        for anio in anios:
            tablas[sigla][anio] = leer_csv(f'{sigla}-{anio}')
    return tablas


def normalizar_columnas(df: pd.DataFrame) -> None:
    """Quita BOM y espacios y pasa a mayúsculas los nombres (in place)."""
    df.columns = (df.columns.str.replace('﻿', '', regex=False)
                  .str.strip().str.upper())


def comparar_columnas(tabla: dict[int, pd.DataFrame], sigla: str,
                      referencia: int = 2026) -> None:
    """Imprime las columnas que difieren del año de referencia (resumido)."""
    columnas_ref = set(tabla[referencia].columns)
    for anio, df in tabla.items():
        if anio == referencia:
            continue
        actuales = set(df.columns)
        faltan = sorted(columnas_ref - actuales)
        sobran = sorted(actuales - columnas_ref)
        if not faltan and not sobran:
            print(f'{sigla}-{anio}: mismas columnas que {referencia}')
            continue
        print(f'{sigla}-{anio}: faltan {len(faltan)}, sobran {len(sobran)}')
        print(f'    faltan: {faltan[:8]}{" ..." if len(faltan) > 8 else ""}')
        print(f'    sobran: {sobran[:8]}{" ..." if len(sobran) > 8 else ""}')
