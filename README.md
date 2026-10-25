### IMT2200 - Introducción a la Ciencia de Datos
## Proyecto semestral: ¿Mide el NEM lo mismo para todos?

## Acerca del repositorio

### ¿Para qué es este repositorio?

En este repositorio recopilaremos de manera grupal los archivos que elaboremos durante el curso de Introducción a Ciencia de Datos en su edición 2026-2. Ya sean tareas, desarrollos o proyectos, subiremos lo que consideremos necesario dentro de este repositorio, somos parte de la única sección del curso :)

### Acerca de nosotros

| Nombre                    | Github                                             | Email asociado                   |
|---------------------------|----------------------------------------------------| ---------------------------------|
| Matías Segovia            | [@msegoviag2007](https://github.com/msegoviag2007) | msegoviag@estudiante.uc.cl       |
| Martín Visciglio          | [@MartinVL8](https://github.com/MartinVL8)         | martinviscigliolabarca@gmail.com |
| Benjamín Saez             | [@benja3617](https://github.com/benja3617)         | benjamn.sez@estudiante.uc.cl     |
| Matías Heresmann          | [@darthvython](https://github.com/darthvython)     | mh.heresmann@gmail.com           |
---
## Proyecto semestral IMT2200: Introducción a la Ciencia de Datos 2026-2 · Grupo 5


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
    ├── limpieza.py          # Decisiones 2 a 4
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
.venv\Scripts\activate       
pip install -r requirements.txt
jupyter lab notebooks/
```

### Uso de herramientas de IA

En este proyecto se usó Claude (Anthropic) como apoyo en la escritura,
simplificación y depuración del código, en la organización del repositorio y en
la documentación. También se usó para revisar resultados y proponer
alternativas metodológicas, como la brecha condicional, que el equipo evaluó
antes de adoptarlas. Todas las decisiones del análisis fueron revisadas y
aprobadas por el equipo.
