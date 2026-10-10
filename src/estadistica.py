"""Funciones estadísticas usadas en el EDA."""
import numpy as np
import pandas as pd
from scipy.stats.contingency import association

from src.config import ELECTIVAS


def resumen(df: pd.DataFrame, grupo: str | list[str],
            variable: str) -> pd.DataFrame:
    """Descriptivos de `variable` por `grupo`, con IC 95% de la media."""
    tabla = df.groupby(grupo, observed=True)[variable].agg(
        n='count', media='mean', de='std', mediana='median')
    error = 1.96 * tabla['de'] / np.sqrt(tabla['n'])
    tabla['ic95_inf'] = tabla['media'] - error
    tabla['ic95_sup'] = tabla['media'] + error
    return tabla.round(3)


def diagnostico_columnas(df: pd.DataFrame,
                         columnas: list[str]) -> pd.DataFrame:
    """Tabla larga con % nulos, % ceros, mínimo y máximo por año y columna."""
    filas = []
    for anio, grupo in df.groupby('ANIO'):
        for col in columnas:
            serie = grupo[col]
            numerica = pd.api.types.is_numeric_dtype(serie)
            filas.append({
                'ANIO': anio,
                'columna': col,
                'pct_nulo': 100 * serie.isna().mean(),
                'pct_cero': 100 * (serie == 0).mean() if numerica else np.nan,
                'min': serie.min() if numerica else np.nan,
                'max': serie.max() if numerica else np.nan,
            })
    return pd.DataFrame(filas)


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
    diferencias se debe a en qué colegio está el estudiante. Es una versión
    simple del ICC (lo sobreestima levemente cuando los colegios son
    pequeños); el ICC exacto saldrá del modelo jerárquico.
    """
    datos = df[[grupo, variable]].dropna()
    promedio_colegio = datos.groupby(grupo)[variable].transform('mean')
    return promedio_colegio.var() / datos[variable].var()


def correlaciones_anio(g: pd.DataFrame,
                       electivas: list[str] = ELECTIVAS) -> pd.Series:
    """Correlación de NEM con cada prueba y con la electiva de cada grupo."""
    fila = {'NEM~Lectora': g['PTJE_NEM'].corr(g['CLEC_1ra']),
            'NEM~M1': g['PTJE_NEM'].corr(g['MATE1_1ra'])}
    for electiva in electivas:
        sub = g[g['electiva'] == electiva]
        fila[f'NEM~{electiva}'] = sub['PTJE_NEM'].corr(sub['PAES_electiva'])
    return pd.Series(fila)


def tasas_acceso(df: pd.DataFrame, grupo: str) -> pd.DataFrame:
    """Tasas (%) de cada etapa del acceso, absolutas y condicionadas."""
    agrupado = df.groupby(grupo, observed=True)
    tabla = pd.DataFrame({
        'n': agrupado.size(),
        'postuló': agrupado['postulo'].mean(),
        'válida': agrupado['postulacion_valida'].mean(),
        'seleccionado': agrupado['seleccionado'].mean(),
        'matriculado': agrupado['matriculado'].mean(),
    })
    tabla['matric. | seleccionado'] = (
        df[df['seleccionado']].groupby(grupo, observed=True)['matriculado']
        .mean())
    tabla['matric. | postuló'] = (
        df[df['postulo']].groupby(grupo, observed=True)['matriculado'].mean())
    columnas = tabla.columns.drop('n')
    tabla[columnas] = (100 * tabla[columnas]).round(1)
    return tabla
