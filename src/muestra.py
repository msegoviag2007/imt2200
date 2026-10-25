"""Muestra analítica y definición única de la brecha NEM-PAES."""
import numpy as np
import pandas as pd

from src.config import (CODIGOS_ENS_REGULAR, COLUMNAS_PUNTAJES,
                        DEPENDENCIA_ETIQUETAS, EGRESO_OFFSET,
                        MODALIDAD_ETIQUETAS, ORDEN_DECIL, ORDEN_DEPENDENCIA,
                        PRUEBAS_PAES, RBD_SIN_ESTABLECIMIENTO, SEXO_ETIQUETAS)


def puntaje_valido(serie: pd.Series) -> pd.Series:
    """True si el puntaje existe y es positivo (0 significa 'no rindió')."""
    return serie.notna() & (serie > 0)


def primera_rendicion(df: pd.DataFrame, prueba: str) -> pd.Series:
    """Puntaje regular del proceso actual; si no rindió, el de invierno."""
    regular = df[f'{prueba}_REG_ACTUAL']
    invierno = df[f'{prueba}_INV_ACTUAL']
    regular = regular.where(puntaje_valido(regular))
    invierno = invierno.where(puntaje_valido(invierno))
    return regular.fillna(invierno)


def construir_muestra(panel: pd.DataFrame
                      ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica los filtros de la muestra y devuelve (muestra, embudo).

    Muestra: egresados recientes, con NEM válido, al menos una electiva y
    educación regular (niños y jóvenes) en un establecimiento identificado.
    Quienes rindieron Ciencias e Historia forman el grupo 'Ambas'.
    """
    df = panel.copy()
    for prueba in PRUEBAS_PAES:
        df[f'{prueba}_1ra'] = primera_rendicion(df, prueba)

    # Grupo de electiva según qué pruebas rindió.
    cien = df['CIEN_1ra'].notna()
    hcsoc = df['HCSOC_1ra'].notna()
    df['electiva'] = 'Ninguna'
    df.loc[cien & ~hcsoc, 'electiva'] = 'Ciencias'
    df.loc[hcsoc & ~cien, 'electiva'] = 'Historia'
    df.loc[cien & hcsoc, 'electiva'] = 'Ambas'

    # Filtros acumulativos: cada paso se aplica sobre el anterior.
    filtros = {
        'Inscritos': pd.Series(True, index=df.index),
        'Egresado reciente':
            df['ANYO_DE_EGRESO'] == df['ANIO'] - EGRESO_OFFSET,
        '+ NEM válido': puntaje_valido(df['PTJE_NEM']),
        '+ rindió electiva': df['electiva'] != 'Ninguna',
        # Excluye validación y reconocimiento de estudios (sin RBD ni
        # código), educación de adultos y el RBD 99999.
        '+ educación regular en establecimiento identificado':
            df['CODIGO_ENS'].isin(CODIGOS_ENS_REGULAR)
            & (df['RBD'] != RBD_SIN_ESTABLECIMIENTO),
    }
    mascara = pd.Series(True, index=df.index)
    embudo = {}
    for paso, filtro in filtros.items():
        mascara &= filtro
        embudo[paso] = mascara.groupby(df['ANIO']).sum()

    # Los puntajes originales ya no se necesitan: quedan las columnas _1ra.
    muestra = df[mascara].drop(columns=COLUMNAS_PUNTAJES)
    # PAES electiva: promedio de las electivas que rindió (si rindió una
    # sola, es ese puntaje; si rindió ambas, el promedio de las dos).
    muestra['PAES_electiva'] = muestra[['CIEN_1ra', 'HCSOC_1ra']].mean(axis=1)
    return muestra, pd.DataFrame(embudo).T


def estandarizar_por_grupo(df: pd.DataFrame, columna: str,
                           grupos: list[str]) -> pd.Series:
    """Puntaje z de `columna` dentro de cada combinación de `grupos`."""
    agrupado = df.groupby(grupos)[columna]
    return ((df[columna] - agrupado.transform('mean'))
            / agrupado.transform('std'))


def calcular_brechas(muestra: pd.DataFrame) -> pd.DataFrame:
    """Agrega NEM_z, PAES_z y las versiones de la brecha.

    - brecha: NEM_z - PAES_z, con z dentro de cada (año, electiva).
    - brecha_cond (medida principal): residuo de una regresión lineal
      simple de NEM_z sobre PAES_z en cada año y electiva, es decir, NEM
      observado menos el esperado dada la PAES.
    - brecha_CLEC / brecha_MATE1: brecha simple con las pruebas
      obligatorias, para el análisis de sensibilidad.
    """
    muestra = muestra.copy()
    grupos = ['ANIO', 'electiva']
    muestra['NEM_z'] = estandarizar_por_grupo(muestra, 'PTJE_NEM', grupos)
    muestra['PAES_z'] = estandarizar_por_grupo(muestra, 'PAES_electiva',
                                               grupos)
    muestra['brecha'] = muestra['NEM_z'] - muestra['PAES_z']

    for _, grupo in muestra.groupby(grupos):
        # Recta NEM_z = pendiente * PAES_z + intercepto en este grupo.
        pendiente, intercepto = np.polyfit(grupo['PAES_z'], grupo['NEM_z'],
                                           deg=1)
        esperado = pendiente * grupo['PAES_z'] + intercepto
        muestra.loc[grupo.index, 'brecha_cond'] = grupo['NEM_z'] - esperado

    for prueba in ['CLEC', 'MATE1']:
        tiene = muestra[f'{prueba}_1ra'].notna()
        sub = muestra[tiene]
        nem_z = estandarizar_por_grupo(sub, 'PTJE_NEM', ['ANIO'])
        paes_z = estandarizar_por_grupo(sub, f'{prueba}_1ra', ['ANIO'])
        muestra.loc[tiene, f'brecha_{prueba}'] = nem_z - paes_z
    return muestra


def agregar_variables(muestra: pd.DataFrame) -> pd.DataFrame:
    """Agrega variables explicativas con etiquetas legibles y orden fijo."""
    muestra = muestra.copy()
    muestra['dependencia'] = pd.Categorical(
        muestra['DEPENDENCIA'].map(DEPENDENCIA_ETIQUETAS),
        categories=ORDEN_DEPENDENCIA, ordered=True)
    # Decil 1 a 10; quienes no declaran ingreso (código 99) quedan como
    # 'No responde' en una categoría propia.
    muestra['decil_num'] = muestra['INGRESO_PERCAPITA_GRUPO_FA']
    etiqueta = (muestra['decil_num'].astype('Int64').astype('string')
                .fillna('No responde'))
    muestra['decil'] = pd.Categorical(etiqueta, categories=ORDEN_DECIL,
                                      ordered=True)
    muestra['modalidad'] = (muestra['RAMA_EDUCACIONAL'].str[0]
                            .map(MODALIDAD_ETIQUETAS))
    muestra['sexo'] = muestra['SEXO'].map(SEXO_ETIQUETAS)
    return muestra
