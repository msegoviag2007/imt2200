"""Limpieza y unificación de las tablas (Decisiones 2 a 6 del notebook 01)."""
import numpy as np
import pandas as pd

from src.config import (CODIGO_NO_RESPONDE_INGRESO, COL_PREFERENCIA,
                        COLUMNAS_NUMERICAS, COLUMNAS_PREF_ANCHO,
                        EGRESO_OFFSET, ESTADOS_SELECCION, ESTADOS_VALIDOS,
                        N_PREFERENCIAS_ANCHO)


# ---------------------------------------------------------------------------
# Decisión 2: postulaciones a una fila por estudiante
# ---------------------------------------------------------------------------
def a_formato_largo(df_ps: pd.DataFrame, anio: int) -> pd.DataFrame:
    """Devuelve PS con una fila por preferencia.

    PS 2024-2026 ya viene en formato largo (una fila por preferencia). PS 2023
    viene en formato ancho: una fila por estudiante con las columnas
    ESTADO_PREF_01 ... ESTADO_PREF_20 (y lo mismo para COD_CARRERA_PREF,
    PTJE_PREF y LUGAR_PREF). Para pasarlo a largo se toma una preferencia a
    la vez, se le quita el sufijo _nn a sus columnas y se apilan las 20.
    """
    if 'ESTADO_PREF' in df_ps.columns:
        print(f'PS-{anio}: formato largo ({len(df_ps)} filas)')
        return df_ps

    # Columnas numeradas (las de las 20 preferencias) y columnas comunes.
    numeradas = [f'{base}_{n:02d}'
                 for n in range(1, N_PREFERENCIAS_ANCHO + 1)
                 for base in COLUMNAS_PREF_ANCHO]
    comunes = [c for c in df_ps.columns if c not in numeradas]

    partes = []
    for n in range(1, N_PREFERENCIAS_ANCHO + 1):
        # Ej.: para n = 3, ESTADO_PREF_03 pasa a llamarse ESTADO_PREF.
        renombre = {f'{base}_{n:02d}': base for base in COLUMNAS_PREF_ANCHO}
        parte = df_ps[comunes + list(renombre)].rename(columns=renombre)
        parte[COL_PREFERENCIA] = n
        partes.append(parte)
    largo = pd.concat(partes, ignore_index=True)

    # Las preferencias vacías vienen con ESTADO_PREF = 0: se eliminan.
    estado = pd.to_numeric(largo['ESTADO_PREF'], errors='coerce')
    largo = largo[estado.notna() & (estado != 0)]
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
                        estados_seleccion: set[int] = ESTADOS_SELECCION
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
    # Cuenta como seleccionado quien tenga algún estado 24 o 26.
    en_seleccion = df['ESTADO_PREF'].isin(estados_seleccion)
    seleccionados = df.loc[en_seleccion, 'MRUN']
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
    # Copia "ordenada" del panel: evita un aviso de rendimiento de pandas
    # al agregarle varias columnas nuevas a una tabla tan ancha.
    panel = panel.copy()
    panel['postulo'] = panel['MRUN'].isin(ps_resumido['MRUN'])
    # Quienes no postularon quedan como NaN tras el merge: pasan a False.
    for col in ['postulacion_valida', 'seleccionado']:
        panel[col] = panel[col].fillna(False).astype(bool)
    panel['matriculado'] = panel['MRUN'].isin(m['MRUN'])
    panel['ANIO'] = anio
    return panel


# ---------------------------------------------------------------------------
# Decisión 4: tipos y datos faltantes
# ---------------------------------------------------------------------------
def forzar_numericas(panel: pd.DataFrame, columnas: list[str], anio: int,
                     verbose: bool = True) -> pd.DataFrame:
    """Convierte columnas a numérico; lo no convertible queda como NaN.

    Algunas columnas vienen como texto por celdas en blanco. En ese caso los
    decimales vienen con coma, así que primero se cambia ',' por '.'.
    """
    panel = panel.copy()
    for col in columnas:
        if col not in panel.columns:
            continue
        if pd.api.types.is_numeric_dtype(panel[col]):
            continue  # ya es numérica
        texto = panel[col].astype(str).str.replace(',', '.')
        convertida = pd.to_numeric(texto, errors='coerce')
        # Valores que existían pero no eran números (p. ej., espacios).
        perdidos = convertida.isna() & panel[col].notna()
        if verbose and perdidos.any():
            ejemplos = list(texto[perdidos].unique()[:3])
            print(f'{anio} | {col}: {perdidos.sum()} valores no numéricos '
                  f'-> NaN (ej.: {ejemplos})')
        panel[col] = convertida.astype('float64')
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
