"""Muestra analítica y definición única de la brecha NEM-PAES."""
import numpy as np
import pandas as pd

from src.config import (COLUMNAS_EDA, CRITERIO_RENDICION,
                        DEPENDENCIA_ETIQUETAS, EGRESO_OFFSET, INCLUIR_AMBAS,
                        MODALIDAD_ETIQUETAS, ORDEN_DECIL, ORDEN_DEPENDENCIA,
                        PRUEBAS_PAES, RBD_SIN_ESTABLECIMIENTO, SEXO_ETIQUETAS)


def puntaje_valido(serie: pd.Series) -> pd.Series:
    """True si el puntaje existe y es positivo (0 suele ser 'no rindió')."""
    return serie.notna() & (serie > 0)


def puntaje_primera_rendicion(df: pd.DataFrame, prueba: str,
                              criterio: str = CRITERIO_RENDICION
                              ) -> pd.Series:
    """Puntaje de la rendición considerada 'primera' según el criterio."""
    reg = df[f'{prueba}_REG_ACTUAL']
    inv = df[f'{prueba}_INV_ACTUAL']
    reg = reg.where(puntaje_valido(reg))
    inv = inv.where(puntaje_valido(inv))
    if criterio == 'regular':
        return reg.fillna(inv)
    if criterio == 'cronologico':
        return inv.fillna(reg)
    raise ValueError(f'Criterio desconocido: {criterio}')


def construir_muestra(panel: pd.DataFrame,
                      criterio: str = CRITERIO_RENDICION,
                      incluir_ambas: bool = INCLUIR_AMBAS
                      ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica los filtros de la muestra y devuelve (muestra, embudo).

    Muestra: egresados recientes, con NEM válido y al menos una electiva.
    Quienes rindieron Ciencias e Historia forman el grupo 'Ambas', con PAES
    electiva igual al promedio de los dos puntajes.
    """
    df = panel[[c for c in COLUMNAS_EDA if c in panel.columns]].copy()
    for prueba in PRUEBAS_PAES:
        df[f'{prueba}_1ra'] = puntaje_primera_rendicion(df, prueba, criterio)

    cien = df['CIEN_1ra'].notna()
    hcsoc = df['HCSOC_1ra'].notna()
    df['electiva'] = np.select(
        [cien & ~hcsoc, hcsoc & ~cien, cien & hcsoc],
        ['Ciencias', 'Historia', 'Ambas'], default='Ninguna')

    # Filtros acumulativos: cada paso se aplica sobre el anterior.
    filtros = {
        'Inscritos': pd.Series(True, index=df.index),
        'Egresado reciente':
            df['ANYO_DE_EGRESO'] == df['ANIO'] - EGRESO_OFFSET,
        '+ NEM válido': puntaje_valido(df['PTJE_NEM']),
        '+ rindió electiva': df['electiva'] != 'Ninguna',
    }
    if not incluir_ambas:
        filtros['+ una sola electiva'] = df['electiva'] != 'Ambas'
    mascara = pd.Series(True, index=df.index)
    embudo = {}
    for paso, filtro in filtros.items():
        mascara &= filtro
        embudo[paso] = mascara.groupby(df['ANIO']).sum()
    embudo = pd.DataFrame(embudo).T

    muestra = df[mascara].copy()
    muestra['PAES_electiva'] = np.select(
        [muestra['electiva'] == 'Ciencias', muestra['electiva'] == 'Historia'],
        [muestra['CIEN_1ra'], muestra['HCSOC_1ra']],
        default=muestra[['CIEN_1ra', 'HCSOC_1ra']].mean(axis=1).to_numpy())
    return muestra, embudo


def estandarizar_por_grupo(df: pd.DataFrame, columna: str,
                           grupos: list[str]) -> pd.Series:
    """Puntaje z de `columna` dentro de cada combinación de `grupos`."""
    agrupado = df.groupby(grupos, observed=True)[columna]
    return ((df[columna] - agrupado.transform('mean'))
            / agrupado.transform('std'))


def calcular_brechas(muestra: pd.DataFrame) -> pd.DataFrame:
    """Agrega NEM_z, PAES_z y las versiones de la brecha.

    - brecha: NEM_z - PAES_z, con z dentro de cada (año, electiva).
    - brecha_cond: NEM_z - r * PAES_z, es decir, NEM observado menos el
      esperado dada la PAES (r = correlación dentro de cada año y electiva).
      Corrige la regresión a la media de la brecha simple.
    - brecha_CLEC / brecha_MATE1: versiones con las pruebas obligatorias,
      para el análisis de sensibilidad.
    """
    muestra = muestra.copy()
    grupos = ['ANIO', 'electiva']
    muestra['NEM_z'] = estandarizar_por_grupo(muestra, 'PTJE_NEM', grupos)
    muestra['PAES_z'] = estandarizar_por_grupo(muestra, 'PAES_electiva',
                                               grupos)
    muestra['brecha'] = muestra['NEM_z'] - muestra['PAES_z']

    r_grupo = (muestra.groupby(grupos)[['NEM_z', 'PAES_z']].corr()
               .xs('PAES_z', level=2)['NEM_z'].rename('r'))
    r_fila = muestra.join(r_grupo, on=grupos)['r']
    muestra['brecha_cond'] = muestra['NEM_z'] - r_fila * muestra['PAES_z']

    for prueba in ['CLEC', 'MATE1']:
        tiene = muestra[f'{prueba}_1ra'].notna()
        sub = muestra.loc[tiene]
        nem_z = estandarizar_por_grupo(sub, 'PTJE_NEM', ['ANIO'])
        paes_z = estandarizar_por_grupo(sub, f'{prueba}_1ra', ['ANIO'])
        muestra.loc[tiene, f'brecha_{prueba}'] = nem_z - paes_z
    return muestra


def agregar_variables(muestra: pd.DataFrame) -> pd.DataFrame:
    """Agrega variables explicativas con etiquetas legibles y orden fijo."""
    muestra = muestra.copy()
    muestra['dependencia'] = pd.Categorical(
        muestra['DEPENDENCIA'].map(DEPENDENCIA_ETIQUETAS).fillna('Sin dato'),
        categories=ORDEN_DEPENDENCIA, ordered=True)

    decil = muestra['INGRESO_PERCAPITA_GRUPO_FA']
    muestra['decil_num'] = decil.where(decil.between(1, 10))
    muestra['decil'] = pd.Categorical(
        np.where(muestra['decil_num'].isna(), 'No responde',
                 muestra['decil_num'].fillna(0).astype(int).astype(str)),
        categories=ORDEN_DECIL, ordered=True)

    muestra['modalidad'] = (muestra['RAMA_EDUCACIONAL'].astype('string')
                            .str[0].map(MODALIDAD_ETIQUETAS)
                            .fillna('Otra / sin dato'))
    muestra['sexo'] = muestra['SEXO'].map(SEXO_ETIQUETAS).fillna('Sin dato')

    # .eq(True) deja NaN como False sin el FutureWarning de fillna.
    for col in ['postulo', 'postulacion_valida', 'seleccionado',
                'matriculado']:
        muestra[col] = muestra[col].eq(True)

    # RBD 99999 no es un colegio: se deja como NaN para el análisis por RBD.
    sin_rbd = muestra['RBD'] == RBD_SIN_ESTABLECIMIENTO
    muestra.loc[sin_rbd, 'RBD'] = np.nan
    return muestra
