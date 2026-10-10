### IMT2200 - Introducción a la Ciencia de Datos
## Proyecto semestral: ¿Mide el NEM lo mismo para todos?

## Acerca del repositorio

### ¿Para qué es este repositorio?

En este repositorio recopilaremos de manera grupal los archivos que elaboremos durante el curso de Introducción a Ciencia de Datos en su edición 2026-2. Ya sean tareas, desarrollos o proyectos, subiremos lo que consideremos necesario dentro de este repositorio, somos parte de la única sección del curso :)

### ¿Qué se encuentra en este repositorio?

Por ahora, no hemos subido ningún archivo, actualizaremos esta sección a medida que vayamos subiendo cada archivo, avance, tarea o proyecto requerido por el curso.

## Acerca de nosotros

### Nuestra información

| Nombre                    | Github                                             | Email asociado                   |
|---------------------------|----------------------------------------------------| ---------------------------------|
| Matías Segovia            | [@msegoviag2007](https://github.com/msegoviag2007) | msegoviag@estudiante.uc.cl       |
| Martín Visciglio          | [@MartinVL8](https://github.com/MartinVL8)         | martinviscigliolabarca@gmail.com |
| Benjamín Saez             | [@benja3617](https://github.com/benja3617)         | benjamn.sez@estudiante.uc.cl     |
| Matías Heresmann          | [@darthvython](https://github.com/darthvython)     | mh.heresmann@gmail.com           |
---
## Proyecto semestral IMT2200: Introducción a la Ciencia de Datos 2026-2 · Grupo 6


Análisis de la brecha entre las notas de enseñanza media (NEM) y la PAES según la
dependencia administrativa del establecimiento y el nivel socioeconómico de los
estudiantes, y de su relación con el acceso a la educación superior (procesos de
admisión 2023-2026, datos abiertos del MINEDUC).

### Estructura

```
proyecto-nem-paes/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── processed/           # panel_completo.parquet y muestra.parquet (no se suben)
├── docs/                    # propuesta, retroalimentación y libros de códigos 2026
├── imgs/                    # figuras (.png) y tablas (.csv) generadas por el EDA
├── notebooks/
│   ├── 01_carga_y_limpieza.ipynb
│   └── 02_eda.ipynb
└── src/                     # código reutilizable de los notebooks
    ├── config.py            # rutas, IDs de Drive, parámetros y etiquetas
    ├── carga.py             # lectura de los CSV directo desde Google Drive
    ├── limpieza.py          # Decisiones 2 a 6
    ├── muestra.py           # muestra analítica y definición de las brechas
    ├── estadistica.py       # resúmenes, varianza entre colegios, V de Cramér,
    │                        # tasas de acceso
    └── graficos.py          # estilo y guardado de figuras
```

### Cómo ejecutar

Los notebooks se corren **en orden**; cada uno deja un archivo que usa el siguiente.

| Notebook | Entrada | Salida |
|---|---|---|
| `01_carga_y_limpieza` | 16 CSV desde Google Drive | `data/processed/panel_completo.parquet` |
| `02_eda` | `panel_completo.parquet` | `data/processed/muestra.parquet` e `imgs/*.png` |

**Local (Jupyter / VS Code)**, con un entorno virtual en la carpeta `.venv/`
(ignorada por git):

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (en macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
jupyter lab notebooks/
```

**Google Colab:** clonar el repositorio y trabajar desde la carpeta `notebooks/`:

```python
!git clone <URL-del-repositorio>
%cd <nombre-del-repositorio>/notebooks
```

`01` lee los 16 CSV directo desde Google Drive en cada ejecución (no se guardan
copias locales), por lo que la carga tarda algunos minutos. Los parámetros que el equipo puede cambiar (criterio de
rendición, inclusión de quienes rinden ambas electivas, códigos de estado, etc.)
están todos en `src/config.py`.

### Uso de herramientas de IA

En este proyecto se usó Claude (Anthropic) como apoyo en la escritura,
simplificación y depuración del código, en la organización del repositorio y en
la documentación. También se usó para revisar resultados y proponer
alternativas metodológicas, como la brecha condicional, que el equipo evaluó
antes de adoptarlas. Todas las decisiones del análisis fueron revisadas y
aprobadas por el equipo.
