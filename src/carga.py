"""Lectura de las 16 tablas del proyecto (4 tipos x 4 años) desde Drive."""
import pandas as pd

from src.config import ANIOS, IDS_DRIVE, TABLAS, URL_DRIVE


def leer_csv(clave: str) -> pd.DataFrame:
    """Lee directo desde Google Drive un CSV como 'IP-2026'.

    Los CSV del MINEDUC usan ';' como separador y coma decimal. Los nombres
    de columnas se limpian (sin BOM ni espacios, en mayúsculas) para que
    sean iguales en todos los años.
    """
    url = URL_DRIVE.format(IDS_DRIVE[clave])
    print(f'Leyendo {clave} desde Google Drive ...')
    df = pd.read_csv(url, sep=';', decimal=',', low_memory=False)
    df.columns = df.columns.str.replace('﻿', '').str.strip().str.upper()
    return df


def cargar_tablas(anios: list[int] = ANIOS
                  ) -> dict[str, dict[int, pd.DataFrame]]:
    """Carga las tablas como {'IP': {2026: df, ...}, 'SD': {...}, ...}."""
    tablas = {}
    for sigla in TABLAS:
        tablas[sigla] = {}
        for anio in anios:
            tablas[sigla][anio] = leer_csv(f'{sigla}-{anio}')
    return tablas


def comparar_columnas(tabla: dict[int, pd.DataFrame], sigla: str,
                      referencia: int = 2026) -> None:
    """Imprime cuántas columnas faltan o sobran respecto del año 2026."""
    columnas_ref = set(tabla[referencia].columns)
    for anio, df in tabla.items():
        faltan = sorted(columnas_ref - set(df.columns))
        sobran = sorted(set(df.columns) - columnas_ref)
        if anio != referencia and (faltan or sobran):
            print(f'{sigla}-{anio}: faltan {len(faltan)} (ej.: {faltan[:3]}), '
                  f'sobran {len(sobran)} (ej.: {sobran[:3]})')
