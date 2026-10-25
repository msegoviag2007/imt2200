"""Estilo y gráficos que se repiten en el EDA."""
import matplotlib.pyplot as plt
import pandas as pd

from src.config import (DEPENDENCIAS_LINEAS, DIR_IMGS, MIN_N_CELDA,
                        ORDEN_DEPENDENCIA)
from src.estadistica import resumen


def aplicar_estilo() -> None:
    """Estilo común para todas las figuras del proyecto."""
    plt.rcParams.update({
        'figure.figsize': (9, 5),
        'figure.dpi': 110,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.spines.top': False,
        'axes.spines.right': False,
        # Signo menos como guion normal (convención del proyecto).
        'axes.unicode_minus': False,
    })


def mostrar(nombre: str) -> None:
    """Guarda la figura actual en imgs/<nombre>.png y la muestra."""
    DIR_IMGS.mkdir(parents=True, exist_ok=True)
    plt.gcf().savefig(DIR_IMGS / f'{nombre}.png', dpi=150,
                      bbox_inches='tight')
    plt.show()


def histogramas(ax: plt.Axes, df: pd.DataFrame, columna: str,
                grupo: str) -> None:
    """Un histograma (solo el contorno) de `columna` por cada `grupo`."""
    for valor, datos in df.groupby(grupo):
        ax.hist(datos[columna], bins=60, histtype='step', density=True,
                label=str(valor))
    ax.set_ylabel('Densidad')


def boxplot_por_dependencia(ax: plt.Axes, df: pd.DataFrame,
                            columna: str) -> None:
    """Una caja de `columna` por dependencia (sin atípicos)."""
    etiquetas = [d for d in ORDEN_DEPENDENCIA
                 if (df['dependencia'] == d).any()]
    cajas = [df.loc[df['dependencia'] == d, columna] for d in etiquetas]
    ax.boxplot(cajas, showfliers=False)
    ax.set_xticks(range(1, len(etiquetas) + 1), etiquetas, rotation=20)
    ax.axhline(0, color='black', linewidth=0.8)


def lineas_por_dependencia(ax: plt.Axes, df: pd.DataFrame, x: str,
                           columna: str, con_ic: bool = False) -> None:
    """Media de `columna` según `x`, una línea por dependencia.

    Con con_ic=True agrega el intervalo de confianza del 95% y omite los
    puntos con menos de MIN_N_CELDA estudiantes.
    """
    for dependencia in DEPENDENCIAS_LINEAS:
        datos = df[df['dependencia'] == dependencia]
        if con_ic:
            tabla = resumen(datos, x, columna)
            tabla = tabla[tabla['n'] >= MIN_N_CELDA]
            error = [tabla['media'] - tabla['ic95_inf'],
                     tabla['ic95_sup'] - tabla['media']]
            ax.errorbar(tabla.index.astype(str), tabla['media'], yerr=error,
                        marker='o', capsize=3, label=dependencia)
        else:
            medias = datos.groupby(x, observed=True)[columna].mean()
            ax.plot(medias.index.astype(str), medias.values, marker='o',
                    label=dependencia)
    ax.legend(fontsize=8)
