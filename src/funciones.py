"""Funciones que usan varios notebooks (se ejecutan desde notebooks/)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Estilo común de las figuras.
plt.rcParams.update({'figure.figsize': (9, 5), 'figure.dpi': 110,
                     'axes.grid': True, 'grid.alpha': 0.3,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.unicode_minus': False})


def mostrar(nombre: str) -> None:
    """Guarda la figura actual en imgs/<nombre>.png y la muestra."""
    plt.savefig(f'../imgs/{nombre}.png', dpi=150, bbox_inches='tight')
    plt.show()


def estandarizar(df: pd.DataFrame, columna: str,
                 grupos: list[str]) -> pd.Series:
    """Puntaje z de `columna` dentro de cada combinación de `grupos`."""
    agrupado = df.groupby(grupos)[columna]
    media = agrupado.transform('mean')
    desviacion = agrupado.transform('std')
    return (df[columna] - media) / desviacion


def preparar_datos(muestra: pd.DataFrame) -> pd.DataFrame:
    """Prepara la muestra para los modelos de los notebooks 03 a 05."""
    datos = muestra.copy()
    # Como texto, statsmodels toma como referencia la primera categoría en
    # orden alfabético: decil 1, Hombre, Científico-humanista y Ambas.
    for col in ['decil', 'sexo', 'modalidad', 'electiva']:
        datos[col] = datos[col].astype(str)
    # Dependencia: Part. subvencionado primero para que sea la referencia.
    datos['dependencia'] = pd.Categorical(
        datos['dependencia'].astype(str),
        categories=['Part. subvencionado', 'Adm. delegada', 'Municipal',
                    'Part. pagado', 'SLEP'])
    # Composición del colegio: decil medio de sus estudiantes (4 años),
    # solo con quienes declaran ingreso.
    datos['decil_medio_colegio'] = (datos.groupby('RBD')['decil_num']
                                    .transform('mean'))
    # Para el acceso: etapas como 0 y 1, tercil de PAES y puntaje ponderado
    # en unidades de 100 puntos (un 0 significa que no hay puntaje).
    for etapa in ['postulo', 'seleccionado', 'matriculado']:
        datos[etapa] = datos[etapa].astype(int)
    datos['tercil_paes'] = pd.qcut(datos['PAES_z'], 3,
                                   labels=['PAES baja', 'PAES media',
                                           'PAES alta'])
    puntaje = datos['ptje_ponderado_max']
    datos['ptje_100'] = puntaje.where(puntaje > 0) / 100
    return datos


def coeficientes(resultado) -> pd.DataFrame:
    """Coeficientes de los efectos fijos con IC 95% y valor p."""
    nombres = resultado.model.exog_names
    ic = resultado.conf_int().loc[nombres]
    return pd.DataFrame({'coef': resultado.params[nombres],
                         'ic95_inf': ic[0], 'ic95_sup': ic[1],
                         'valor_p': resultado.pvalues[nombres]})


def odds_ratios(resultado) -> pd.DataFrame:
    """Odds ratio (exponencial del coeficiente) con IC 95% y valor p."""
    tabla = coeficientes(resultado)
    for col in ['coef', 'ic95_inf', 'ic95_sup']:
        tabla[col] = np.exp(tabla[col])
    return tabla.rename(columns={'coef': 'odds_ratio'})


def icc(resultado) -> float:
    """Varianza entre colegios sobre la varianza total."""
    entre = resultado.cov_re.iloc[0, 0]
    return float(entre / (entre + resultado.scale))


def contraste(resultado, a: str, b: str) -> pd.Series:
    """Diferencia entre dos coeficientes (a - b) con IC 95%."""
    # Un peso por coeficiente: +1 para a, -1 para b y 0 para el resto.
    nombres = list(resultado.fe_params.index)
    pesos = np.zeros((1, len(nombres)))
    pesos[0, nombres.index(a)] = 1
    pesos[0, nombres.index(b)] = -1
    prueba = resultado.t_test(pesos)
    inferior, superior = prueba.conf_int()[0]
    return pd.Series({'diferencia': float(prueba.effect[0]),
                      'ic95_inf': inferior, 'ic95_sup': superior})
