"""Limpieza y unificación de las tablas (Decisiones 2 a 4 del notebook 01)."""
import numpy as np
import pandas as pd

from src.config import (CODIGO_NO_RESPONDE_INGRESO, COLUMNAS_NUMERICAS,
                        COLUMNAS_PREF_ANCHO, ESTADOS_SELECCION,
                        ESTADOS_VALIDOS, N_PREFERENCIAS_ANCHO)


def a_numero(serie: pd.Series) -> pd.Series:
    """Convierte a número; lo que no es número (p. ej., ' ') queda NaN.

    Si la columna quedó como texto, los decimales vienen con coma, así que
    primero se cambia ',' por '.'.
    """
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype('float64')
    texto = serie.astype(str).str.replace(',', '.')
    return pd.to_numeric(texto, errors='coerce').astype('float64')


# ---------------------------------------------------------------------------
# Decisión 2: postulaciones a una fila por estudiante
# ---------------------------------------------------------------------------
def a_formato_largo(df_ps: pd.DataFrame) -> pd.DataFrame:
    """Devuelve PS con una fila por preferencia.

    PS 2024-2026 ya viene así. PS 2023 viene en formato ancho (una fila por
    estudiante con ESTADO_PREF_01 ... ESTADO_PREF_20, y lo mismo para las
    otras columnas de la preferencia): se toma una preferencia a la vez, se
    le quita el sufijo _nn a sus columnas y se apilan las 20.
    """
    if 'ESTADO_PREF' in df_ps.columns:
        return df_ps
    partes = []
    for n in range(1, N_PREFERENCIAS_ANCHO + 1):
        # Ej.: para n = 3, ESTADO_PREF_03 pasa a llamarse ESTADO_PREF.
        renombre = {f'{base}_{n:02d}': base for base in COLUMNAS_PREF_ANCHO}
        partes.append(df_ps[['MRUN'] + list(renombre)].rename(
            columns=renombre))
    largo = pd.concat(partes, ignore_index=True)
    # Las preferencias vacías vienen con ESTADO_PREF = 0: se eliminan.
    estado = pd.to_numeric(largo['ESTADO_PREF'], errors='coerce')
    return largo[estado.notna() & (estado != 0)]


def resumir_postulacion(df_ps: pd.DataFrame) -> pd.DataFrame:
    """Reduce la postulación a una fila por estudiante (MRUN).

    - postulacion_valida: alguna preferencia en selección o espera.
    - seleccionado: alguna preferencia en estado 24 o 26.
    - ptje_ponderado_max: mayor puntaje ponderado entre sus preferencias.
    """
    estado = pd.to_numeric(df_ps['ESTADO_PREF'], errors='coerce')
    resumen = pd.DataFrame({
        'MRUN': df_ps['MRUN'],
        'postulacion_valida': estado.isin(ESTADOS_VALIDOS),
        'seleccionado': estado.isin(ESTADOS_SELECCION),
        'ptje_ponderado_max': a_numero(df_ps['PTJE_PREF']),
    })
    # El máximo de True/False por estudiante es "alguna preferencia cumple".
    return resumen.groupby('MRUN', as_index=False).max()


# ---------------------------------------------------------------------------
# Decisiones 3 y 4: panel por año, tipos y no respuesta de ingreso
# ---------------------------------------------------------------------------
def armar_panel(ip: pd.DataFrame, sd: pd.DataFrame,
                ps_resumido: pd.DataFrame, m: pd.DataFrame,
                anio: int) -> pd.DataFrame:
    """Une IP, SD, PS (resumida) y M en un panel a nivel estudiante.

    IP es el universo de inscritos, así que los merge son 'left' para no
    perder a quienes no postularon o no se matricularon.
    """
    panel = ip.merge(sd, on='MRUN', how='left', suffixes=('', '_sd'))
    panel = panel.merge(ps_resumido, on='MRUN', how='left')
    # Copia "ordenada": evita un aviso de rendimiento de pandas al agregar
    # columnas nuevas a una tabla tan ancha.
    panel = panel.copy()
    panel['postulo'] = panel['MRUN'].isin(ps_resumido['MRUN'])
    # Quienes no postularon quedan como NaN tras el merge: pasan a False.
    for col in ['postulacion_valida', 'seleccionado']:
        panel[col] = panel[col].fillna(False).astype(bool)
    panel['matriculado'] = panel['MRUN'].isin(m['MRUN'])
    panel['ANIO'] = anio
    return panel


def limpiar_panel(panel: pd.DataFrame
                  ) -> tuple[pd.DataFrame, dict[str, int]]:
    """Fuerza a número las columnas clave y recodifica el ingreso 99.

    Devuelve el panel y, por columna, cuántos valores no eran números (en
    la práctica, celdas con un espacio) y quedaron como NaN.
    """
    panel = panel.copy()
    perdidos = {}
    for col in COLUMNAS_NUMERICAS:
        if col in panel.columns:
            convertida = a_numero(panel[col])
            perdidos[col] = int((convertida.isna() & panel[col].notna()).sum())
            panel[col] = convertida
    ingreso = panel['INGRESO_PERCAPITA_GRUPO_FA']
    panel['INGRESO_PERCAPITA_GRUPO_FA'] = ingreso.replace(
        CODIGO_NO_RESPONDE_INGRESO, np.nan)
    return panel, perdidos
