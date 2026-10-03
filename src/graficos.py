"""Estilo y utilidades de gráficos compartidas por los notebooks."""
import matplotlib.pyplot as plt
import pandas as pd

from src.config import DIR_IMGS, GUARDAR_FIGURAS, MIN_N_CELDA


def aplicar_estilo() -> None:
    """Estilo común para todas las figuras del proyecto."""
    plt.rcParams.update({
        'figure.figsize': (9, 5),
        'figure.dpi': 110,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.spines.top': False,
        'axes.spines.right': False,
    })


def graficar_medias(tabla: pd.DataFrame, ax: plt.Axes,
                    etiqueta: str | None = None) -> None:
    """Grafica medias con IC 95% a partir de la salida de resumen()."""
    tabla = tabla[tabla['n'] >= MIN_N_CELDA]
    x = [str(i) for i in tabla.index]
    error = [tabla['media'] - tabla['ic95_inf'],
             tabla['ic95_sup'] - tabla['media']]
    ax.errorbar(x, tabla['media'], yerr=error, marker='o', capsize=3,
                label=etiqueta)


def mostrar(nombre: str, guardar: bool = GUARDAR_FIGURAS) -> None:
    """Guarda la figura actual en imgs/<nombre>.png y la muestra."""
    if guardar:
        DIR_IMGS.mkdir(parents=True, exist_ok=True)
        plt.gcf().savefig(DIR_IMGS / f'{nombre}.png', dpi=150,
                          bbox_inches='tight')
    plt.show()
