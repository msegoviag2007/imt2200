"""Funciones estadísticas usadas en el EDA."""
import numpy as np
import pandas as pd
from scipy.stats.contingency import association

from src.config import ELECTIVAS


def resumen(df: pd.DataFrame, grupo: str, variable: str) -> pd.DataFrame:
    """Descriptivos de `variable` por `grupo`, con IC 95% de la media."""
    tabla = df.groupby(grupo, observed=True)[variable].agg(
        n='count', media='mean', de='std')
    error = 1.96 * tabla['de'] / np.sqrt(tabla['n'])
    tabla['ic95_inf'] = tabla['media'] - error
    tabla['ic95_sup'] = tabla['media'] + error
    return tabla.round(3)


def nulos_y_ceros(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """% de nulos y de ceros de cada columna (fila) por año (columna)."""
    por_anio = {}
    for anio, grupo in df.groupby('ANIO'):
        fila = {}
        for col in columnas:
            fila[f'{col} (% nulos)'] = 100 * grupo[col].isna().mean()
            fila[f'{col} (% ceros)'] = 100 * (grupo[col] == 0).mean()
        por_anio[anio] = fila
    return pd.DataFrame(por_anio).round(1)


def v_de_cramer(tabla: pd.DataFrame) -> float:
    """V de Cramér de una tabla de contingencia (función de scipy).

    Va de 0 (independencia) a 1 (asociación perfecta).
    """
    return float(association(tabla.to_numpy(), method='cramer'))


def proporcion_varianza_entre(df: pd.DataFrame, variable: str,
                              grupo: str) -> float:
    """Proporción de la varianza de `variable` que ocurre entre `grupo`.

    A cada estudiante se le asigna el promedio de su colegio; la varianza de
    esos promedios dividida por la varianza total indica qué parte de las
    diferencias se debe al colegio. Es una versión simple del ICC (lo
    sobreestima levemente); el ICC exacto saldrá del modelo jerárquico.
    """
    datos = df[[grupo, variable]].dropna()
    promedio_colegio = datos.groupby(grupo)[variable].transform('mean')
    return promedio_colegio.var() / datos[variable].var()


def correlaciones_anio(g: pd.DataFrame) -> pd.Series:
    """Correlación de NEM con Lectora, M1 y la electiva de cada grupo."""
    fila = {'NEM~Lectora': g['PTJE_NEM'].corr(g['CLEC_1ra']),
            'NEM~M1': g['PTJE_NEM'].corr(g['MATE1_1ra'])}
    for electiva in ELECTIVAS:
        sub = g[g['electiva'] == electiva]
        fila[f'NEM~{electiva}'] = sub['PTJE_NEM'].corr(sub['PAES_electiva'])
    return pd.Series(fila)


def tasas_acceso(df: pd.DataFrame, grupo: str) -> pd.DataFrame:
    """Tasas (%) de cada etapa del acceso y matrícula dado seleccionado."""
    agrupado = df.groupby(grupo, observed=True)
    tabla = 100 * agrupado[['postulo', 'postulacion_valida', 'seleccionado',
                            'matriculado']].mean()
    seleccionados = df[df['seleccionado']].groupby(grupo, observed=True)
    tabla['matric. | seleccionado'] = (100 * seleccionados['matriculado']
                                       .mean())
    tabla.insert(0, 'n', agrupado.size())
    tabla = tabla.rename(columns={'postulo': 'postuló',
                                  'postulacion_valida': 'válida'})
    return tabla.round(1)
