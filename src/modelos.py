"""Funciones del modelamiento jerárquico (notebook 03)."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from patsy import dmatrix
from statsmodels.stats.outliers_influence import variance_inflation_factor


def preparar_datos(muestra: pd.DataFrame) -> pd.DataFrame:
    """Deja las variables categóricas como texto y agrega la composición
    socioeconómica del colegio.

    decil_medio_colegio: promedio del decil de los estudiantes del colegio
    (4 años juntos), calculado solo con quienes declaran ingreso.
    """
    datos = muestra.copy()
    for col in ['dependencia', 'decil', 'sexo', 'modalidad', 'electiva']:
        datos[col] = datos[col].astype(str)
    datos['decil_medio_colegio'] = (datos.groupby('RBD')['decil_num']
                                    .transform('mean'))
    return datos


def calcular_vif(datos: pd.DataFrame, variables: str) -> pd.Series:
    """VIF de cada columna de la matriz de diseño (sin el intercepto).

    Cada variable categórica aporta una columna por categoría (salvo la de
    referencia), y cada columna tiene su propio VIF.
    """
    matriz = dmatrix(variables, datos, return_type='dataframe')
    vif = [variance_inflation_factor(matriz.values, i)
           for i in range(1, matriz.shape[1])]
    return pd.Series(vif, index=matriz.columns[1:]).round(2)


def ajustar_mixto(datos: pd.DataFrame, formula: str,
                  pendiente_aleatoria: bool = False,
                  metodo: str | None = None):
    """Modelo mixto con intercepto aleatorio por colegio (RBD), por REML.

    Con pendiente_aleatoria=True, la pendiente de PAES_z también varía
    entre colegios. `metodo` permite elegir otro optimizador (por ejemplo,
    'powell') si el de statsmodels por defecto no converge.
    """
    re_formula = '~PAES_z' if pendiente_aleatoria else None
    modelo = smf.mixedlm(formula, datos, groups=datos['RBD'],
                         re_formula=re_formula)
    if metodo is None:
        return modelo.fit(reml=True)
    return modelo.fit(reml=True, method=metodo)


def icc(resultado) -> float:
    """Varianza del colegio (intercepto) sobre la varianza total."""
    var_colegio = float(resultado.cov_re.iloc[0, 0])
    return var_colegio / (var_colegio + resultado.scale)


def nombre_corto(termino: str) -> str:
    """Nombre legible de un término del modelo.

    Ej.: 'C(sexo)[T.Mujer]' -> 'Mujer', 'C(decil, ...)[T.3]' -> 'decil 3' y
    'PAES_z:C(electiva)[T.Ciencias]' -> 'PAES_z x Ciencias'.
    """
    if '[T.' not in termino:
        return termino
    variable, categoria = termino.split('[T.')
    categoria = categoria.rstrip(']')
    if variable.startswith('PAES_z:'):
        return f'PAES_z x {categoria}'
    for clave, etiqueta in [('decil', 'decil'), ('ANIO', 'año'),
                            ('electiva', 'electiva')]:
        if clave in variable:
            return f'{etiqueta} {categoria}'
    return categoria


def tabla_coeficientes(resultado, contiene: str) -> pd.DataFrame:
    """Coeficientes con IC 95% y valor p de los términos que contienen
    `contiene` (por ejemplo, 'dependencia')."""
    ic = resultado.conf_int()
    terminos = [t for t in resultado.fe_params.index if contiene in t]
    tabla = pd.DataFrame({
        'coef': resultado.fe_params[terminos],
        'ic95_inf': ic.loc[terminos, 0],
        'ic95_sup': ic.loc[terminos, 1],
        'valor_p': resultado.pvalues[terminos],
    })
    tabla.index = [nombre_corto(t) for t in terminos]
    return tabla


def contraste(resultado, termino_a: str, termino_b: str) -> pd.Series:
    """Diferencia entre dos coeficientes (a - b), con IC 95% y valor p."""
    # Una fila con un peso por efecto fijo: +1 para a, -1 para b y 0 para
    # el resto, de modo que la prueba evalúa a - b.
    terminos = list(resultado.fe_params.index)
    pesos = np.zeros((1, len(terminos)))
    pesos[0, terminos.index(termino_a)] = 1
    pesos[0, terminos.index(termino_b)] = -1
    prueba = resultado.t_test(pesos)
    inf, sup = prueba.conf_int()[0]
    return pd.Series({'diferencia': float(prueba.effect[0]),
                      'ic95_inf': inf, 'ic95_sup': sup,
                      'valor_p': float(prueba.pvalue)})


def ajustar_logit(datos: pd.DataFrame, formula: str):
    """Regresión logística con errores estándar agrupados por colegio.

    Los estudiantes de un mismo colegio no son independientes; agrupar los
    errores por RBD corrige los intervalos de confianza sin cambiar los
    coeficientes.
    """
    modelo = smf.logit(formula, datos)
    return modelo.fit(disp=False, cov_type='cluster',
                      cov_kwds={'groups': datos['RBD']})


def tabla_odds_ratios(resultado, terminos: list[str]) -> pd.DataFrame:
    """Odds ratio (exponencial del coeficiente) con IC 95% y valor p.

    Un odds ratio mayor que 1 indica más chances del resultado; menor que
    1, menos chances.
    """
    ic = resultado.conf_int().loc[terminos]
    tabla = pd.DataFrame({
        'odds_ratio': np.exp(resultado.params[terminos]),
        'ic95_inf': np.exp(ic[0]),
        'ic95_sup': np.exp(ic[1]),
        'valor_p': resultado.pvalues[terminos],
    })
    tabla.index = [nombre_corto(t) for t in terminos]
    return tabla
