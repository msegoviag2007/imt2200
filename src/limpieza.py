"""Limpieza y unificación de las tablas (Decisiones 2 a 6 del notebook 01)."""
import re

import numpy as np
import pandas as pd

from src.config import (CODIGO_NO_RESPONDE_INGRESO, COL_PREFERENCIA,
                        COLUMNAS_NUMERICAS, COLUMNAS_PREF, EGRESO_OFFSET,
                        ESTADO_SELECCIONADO, ESTADOS_VALIDOS)

# Nombre que termina en número de preferencia: ESTADO_PREF_01, PTJE_PREF3...
PATRON_ANCHO = re.compile(r'^(.+?)_?(\d{1,2})$')


# ---------------------------------------------------------------------------
# Decisión 2: postulaciones a una fila por estudiante
# ---------------------------------------------------------------------------
def a_formato_largo(df_ps: pd.DataFrame, anio: int,
                    verbose: bool = True) -> pd.DataFrame:
    """Devuelve PS con una fila por preferencia, sea cual sea su formato.

    PS 2024-2026 viene en formato largo (una fila por preferencia); PS 2023
    viene en formato ancho (ESTADO_PREF_01 ... ESTADO_PREF_20).
    """
    if 'ESTADO_PREF' in df_ps.columns:
        if verbose:
            print(f'PS-{anio}: formato largo ({len(df_ps)} filas)')
        return df_ps

    # Agrupa las columnas numeradas por su nombre base.
    numeradas: dict[str, tuple[str, int]] = {}
    for col in df_ps.columns:
        coincide = PATRON_ANCHO.match(col)
        if coincide:
            base = coincide.group(1).rstrip('_')
            if base not in COLUMNAS_PREF and f'{base}_PREF' in COLUMNAS_PREF:
                base = f'{base}_PREF'           # p. ej. ESTADO_01 -> ESTADO
            numeradas[col] = (base, int(coincide.group(2)))
    # Solo cuentan como formato ancho las bases que se repiten 2+ veces.
    conteo = pd.Series([b for b, _ in numeradas.values()]).value_counts()
    bases = set(conteo[conteo > 1].index)
    numeradas = {c: v for c, v in numeradas.items() if v[0] in bases}

    if 'ESTADO_PREF' not in bases:
        candidatas = [c for c in df_ps.columns if 'ESTADO' in c or 'PREF' in c]
        raise KeyError(f'PS-{anio} no tiene ESTADO_PREF ni ESTADO_PREF_n. '
                       f'Columnas candidatas: {candidatas[:15]}')

    ids = [c for c in df_ps.columns if c not in numeradas]
    partes = []
    for numero in sorted({n for _, n in numeradas.values()}):
        renombre = {c: b for c, (b, n) in numeradas.items() if n == numero}
        parte = df_ps[ids + list(renombre)].rename(columns=renombre)
        if COL_PREFERENCIA not in bases:
            parte[COL_PREFERENCIA] = numero
        partes.append(parte)
    largo = pd.concat(partes, ignore_index=True)

    # Quita las preferencias vacías: en 2023 vienen con ESTADO_PREF = 0.
    largo = largo.dropna(subset=sorted(bases - {COL_PREFERENCIA}), how='all')
    estado = pd.to_numeric(largo['ESTADO_PREF'], errors='coerce')
    largo = largo[(estado.isna() | (estado != 0))
                  & largo['ESTADO_PREF'].notna()]
    if verbose:
        print(f'PS-{anio}: formato ancho ({len(df_ps)} filas) -> '
              f'largo ({len(largo)} filas)')
    return largo


def unificar_codigos(df_ps: pd.DataFrame) -> pd.DataFrame:
    """Deja ESTADO_PREF como entero si todos sus códigos son numéricos.

    En formato ancho las columnas vacías vuelven los códigos float (3.0) y
    en otros años pueden venir como texto ('3'); así quedan comparables.
    """
    df_ps = df_ps.copy()
    numerico = pd.to_numeric(df_ps['ESTADO_PREF'], errors='coerce')
    if numerico.notna().sum() == df_ps['ESTADO_PREF'].notna().sum():
        df_ps['ESTADO_PREF'] = numerico.round().astype('Int64')
    return df_ps


def resumir_postulacion(df_ps: pd.DataFrame,
                        estados_validos: set[int] = ESTADOS_VALIDOS,
                        estado_seleccionado: int = ESTADO_SELECCIONADO
                        ) -> pd.DataFrame:
    """Reduce la tabla de postulación a una fila por MRUN.

    Prioriza la preferencia de mejor ubicación (menor ORDEN_PREF) entre las
    de estado válido; si un estudiante no tiene ninguna válida, conserva su
    mejor preferencia inválida para no perder el hecho de que postuló.
    """
    df = df_ps.copy()
    df['postulacion_valida'] = df['ESTADO_PREF'].isin(estados_validos)

    validas = df[df['postulacion_valida']].sort_values(COL_PREFERENCIA)
    mejor_valida = validas.drop_duplicates(subset='MRUN', keep='first')

    sin_valida = ~df['MRUN'].isin(mejor_valida['MRUN'])
    invalidas = df[sin_valida].sort_values(COL_PREFERENCIA)
    mejor_invalida = invalidas.drop_duplicates(subset='MRUN', keep='first')

    resumen = pd.concat([mejor_valida, mejor_invalida], ignore_index=True)
    # 'seleccionado' se calcula aparte: la mejor preferencia válida puede ser
    # una lista de espera ubicada sobre la preferencia en que quedó.
    seleccionados = df.loc[df['ESTADO_PREF'] == estado_seleccionado, 'MRUN']
    resumen['seleccionado'] = resumen['MRUN'].isin(seleccionados)
    return resumen


# ---------------------------------------------------------------------------
# Decisión 3: panel por año
# ---------------------------------------------------------------------------
def armar_panel(ip: pd.DataFrame, sd: pd.DataFrame,
                ps_resumido: pd.DataFrame, m: pd.DataFrame,
                anio: int) -> pd.DataFrame:
    """Fusiona IP, SD, PS (resumida) y M en un panel a nivel estudiante.

    IP es el universo de inscritos, así que todos los merge son 'left' para
    no perder a quienes no postularon o no se matricularon.
    """
    panel = ip.merge(sd, on='MRUN', how='left', suffixes=('', '_sd'))
    panel = panel.merge(ps_resumido, on='MRUN', how='left',
                        suffixes=('', '_ps'))
    panel['postulo'] = panel['MRUN'].isin(ps_resumido['MRUN'])
    # Quienes no postularon quedan como NaN tras el merge: pasan a False.
    for col in ['postulacion_valida', 'seleccionado']:
        panel[col] = panel[col].eq(True)
    panel['matriculado'] = panel['MRUN'].isin(m['MRUN'])
    panel['ANIO'] = anio
    return panel


# ---------------------------------------------------------------------------
# Decisión 4: tipos y datos faltantes
# ---------------------------------------------------------------------------
def forzar_numericas(panel: pd.DataFrame, columnas: list[str], anio: int,
                     verbose: bool = True) -> pd.DataFrame:
    """Convierte columnas a numérico; lo no convertible queda como NaN."""
    panel = panel.copy()
    for col in columnas:
        if col not in panel.columns:
            continue
        original = panel[col]
        if pd.api.types.is_numeric_dtype(original):
            continue
        # Si la columna quedó como texto, los decimales vienen con coma.
        texto = original.astype('string').str.strip().str.replace(
            ',', '.', regex=False)
        # float64 (no Int64/Float64) para que los NaN no rompan los filtros.
        convertida = pd.to_numeric(texto, errors='coerce').astype('float64')
        perdidos = convertida.isna() & original.notna()
        if verbose and perdidos.any():
            ejemplos = texto[perdidos].value_counts().head(3).index.tolist()
            print(f'{anio} | {col}: {perdidos.sum()} valores no numéricos '
                  f'-> NaN (ej.: {ejemplos})')
        panel[col] = convertida
    return panel


def limpiar_panel(panel: pd.DataFrame, anio: int,
                  verbose: bool = True) -> pd.DataFrame:
    """Fuerza tipos numéricos y recodifica la no respuesta de ingreso."""
    panel = forzar_numericas(panel, COLUMNAS_NUMERICAS, anio, verbose)
    panel['INGRESO_PERCAPITA_GRUPO_FA'] = (
        panel['INGRESO_PERCAPITA_GRUPO_FA']
        .replace(CODIGO_NO_RESPONDE_INGRESO, np.nan))
    return panel


# ---------------------------------------------------------------------------
# Decisiones 5 y 6: egreso reciente y concatenación
# ---------------------------------------------------------------------------
def marcar_egreso_reciente(panel: pd.DataFrame, anio: int,
                           offset: int = EGRESO_OFFSET) -> pd.DataFrame:
    """Agrega 'egresado_reciente': egresó el año en que rindió la PAES."""
    panel = panel.copy()
    panel['egresado_reciente'] = panel['ANYO_DE_EGRESO'] == anio - offset
    return panel


def diferencias_columnas(paneles: dict[int, pd.DataFrame],
                         referencia: int = 2023) -> dict[int, set[str]]:
    """Columnas que difieren entre cada panel y el del año de referencia."""
    base = set(paneles[referencia].columns)
    return {a: base ^ set(p.columns)
            for a, p in paneles.items() if a != referencia}
