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
│   ├── raw/                 # CSV originales (se descargan solos; no se suben)
│   └── processed/           # panel_completo.parquet y muestra.parquet (no se suben)
├── docs/                    # propuesta y retroalimentación de la Entrega 1
├── imgs/                    # figuras generadas por el EDA
├── notebooks/
│   ├── 01_carga_y_limpieza.ipynb
│   └── 02_eda.ipynb
└── src/                     # código reutilizable de los notebooks
    ├── config.py            # rutas, IDs de Drive, parámetros y etiquetas
    ├── carga.py             # descarga (con caché) y lectura de los CSV
    ├── limpieza.py          # Decisiones 2 a 6
    ├── muestra.py           # muestra analítica y definición de las brechas
    ├── estadistica.py       # resúmenes, ICC, V de Cramér, tasas de acceso
    └── graficos.py          # estilo y guardado de figuras
```

### Cómo ejecutar

Los notebooks se corren **en orden**; cada uno deja un archivo que usa el siguiente.

| Notebook | Entrada | Salida |
|---|---|---|
| `01_carga_y_limpieza` | 16 CSV desde Google Drive | `data/processed/panel_completo.parquet` |
| `02_eda` | `panel_completo.parquet` | `data/processed/muestra.parquet` e `imgs/*.png` |

**Local (Jupyter / VS Code):**

```bash
pip install -r requirements.txt
jupyter lab notebooks/
```

**Google Colab:** clonar el repositorio y trabajar desde la carpeta `notebooks/`:

```python
!git clone <URL-del-repositorio>
%cd <nombre-del-repositorio>/notebooks
```

La primera ejecución de `01` descarga los 16 CSV a `data/raw/`; las siguientes los
leen desde el disco. Los parámetros que el equipo puede cambiar (criterio de
rendición, inclusión de quienes rinden ambas electivas, códigos de estado, etc.)
están todos en `src/config.py`.

### Estado del proyecto

- [x] Propuesta (Entrega 1): retroalimentación en `docs/`
- [x] Carga, homologación entre años y limpieza de las 16 tablas
- [x] EDA: calidad de datos, muestra, brechas, preguntas 1 a 3, nivel colegio, evolución
- [ ] Confirmar con el equipo la medida principal de la brecha (simple vs. condicional)
- [ ] Modelo jerárquico (estudiantes dentro de establecimientos)
- [ ] Modelos de acceso por etapas (postulación, selección, matrícula)
- [ ] Integración de resultados, visualizaciones finales y video

### Decisiones principales

1. **Unicidad de `MRUN`:** IP, SD y M tienen una fila por estudiante; PS, una por preferencia.
2. **Homologación (1b):** PS-2023 viene en formato ancho y se pasa a formato largo.
3. **Postulación:** una fila por estudiante; `24` = seleccionado y `25` = lista de
   espera (inferidos de los conteos, **por verificar** con el libro de códigos).
4. **Panel:** IP como base y `merge` `left`, para no perder a quienes no postulan.
5. **Tipos y faltantes:** columnas clave forzadas a numérico; código 99 de ingreso
   como "no responde" (categoría propia, no se eliminan filas).
6. **Muestra:** egresados del año de rendición (`ANYO_DE_EGRESO = ANIO - 1`), con NEM
   válido y al menos una electiva; quienes rinden ambas forman su propio grupo.
7. **Brecha:** se calcula una sola vez en `src/muestra.py`, en dos versiones:
   simple (`NEM_z - PAES_z`) y condicional (NEM observado - esperado dada la PAES).

### Pendientes por verificar

- Significado de los códigos de `ESTADO_PREF`, `DEPENDENCIA`, `SEXO` y del RBD `99999`
  en el diccionario de datos del DEMRE/MINEDUC.
- Condiciones de uso y anonimización de los datos abiertos del MINEDUC (pedido en la
  retroalimentación).
- Referencias para las cifras de contexto (20% → 41% de promedios sobre 6,0 y la
  reforma al Ranking 2028).
