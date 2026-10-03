"""Funciones estadísticas usadas en el EDA."""
import numpy as np
import pandas as pd

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
    """V de Cramér de una tabla de contingencia (0 = independencia)."""
    observado = tabla.to_numpy(dtype=float)
    total = observado.sum()
    esperado = (np.outer(observado.sum(axis=1), observado.sum(axis=0))
                / total)
    chi2 = ((observado - esperado) ** 2 / esperado).sum()
    k = min(observado.shape) - 1
    return float(np.sqrt(chi2 / (total * k)))


def icc_anova(df: pd.DataFrame, variable: str, grupo: str) -> float:
    """ICC(1) por ANOVA de una vía, con grupos de tamaño desigual."""
    datos = df[[grupo, variable]].dropna()
    agrupado = datos.groupby(grupo)[variable]
    n_i = agrupado.size()
    k, n_total = len(n_i), n_i.sum()
    media_total = datos[variable].mean()
    ss_entre = (n_i * (agrupado.mean() - media_total) ** 2).sum()
    ss_dentro = ((datos[variable] - agrupado.transform('mean')) ** 2).sum()
    ms_entre = ss_entre / (k - 1)
    ms_dentro = ss_dentro / (n_total - k)
    n0 = (n_total - (n_i ** 2).sum() / n_total) / (k - 1)
    var_entre = max((ms_entre - ms_dentro) / n0, 0)
    return var_entre / (var_entre + ms_dentro)


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
