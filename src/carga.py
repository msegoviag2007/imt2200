"""Descarga y lectura de las 16 tablas del proyecto (4 tipos x 4 años)."""
import urllib.request
from pathlib import Path

import pandas as pd

from src.config import ANIOS, DIR_DATOS_CRUDOS, IDS_DRIVE, TABLAS, URL_DRIVE


def url_drive(clave: str) -> str:
    """URL de descarga directa en Drive para una clave como 'IP-2026'."""
    return URL_DRIVE.format(IDS_DRIVE[clave])


def leer_csv(fuente: str | Path, **kwargs) -> pd.DataFrame:
    """Lee un CSV del MINEDUC (separador ';' y decimales con coma)."""
    return pd.read_csv(fuente, sep=';', decimal=',', low_memory=False,
                       **kwargs)


def obtener_fuente(clave: str, usar_cache: bool = True) -> str | Path:
    """Ruta local del CSV (descargándolo si falta) o su URL si no hay caché.

    Con caché, cada archivo se descarga una sola vez a data/raw/ y las
    siguientes ejecuciones lo leen desde el disco.
    """
    if not usar_cache:
        return url_drive(clave)
    ruta = DIR_DATOS_CRUDOS / f'{clave}.csv'
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta.with_suffix('.part')
        print(f'Descargando {clave} ...')
        urllib.request.urlretrieve(url_drive(clave), temporal)
        temporal.rename(ruta)  # solo queda el CSV si la descarga terminó
    return ruta


def cargar_tablas(anios: list[int] = ANIOS,
                  usar_cache: bool = True
                  ) -> dict[str, dict[int, pd.DataFrame]]:
    """Carga las tablas como {'IP': {2026: df, ...}, 'SD': {...}, ...}."""
    return {
        sigla: {a: leer_csv(obtener_fuente(f'{sigla}-{a}', usar_cache))
                for a in anios}
        for sigla in TABLAS
    }


def normalizar_columnas(df: pd.DataFrame) -> None:
    """Quita BOM y espacios y pasa a mayúsculas los nombres (in place)."""
    df.columns = (df.columns.str.replace('\ufeff', '', regex=False)
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
