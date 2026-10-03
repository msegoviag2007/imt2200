"""Rutas, fuentes de datos y constantes compartidas por los notebooks.

Todos los parámetros que el equipo puede querer cambiar están aquí, para que
los notebooks y los módulos usen siempre los mismos valores.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------
RAIZ: Path = Path(__file__).resolve().parents[1]
DIR_DATOS_CRUDOS: Path = RAIZ / 'data' / 'raw'
DIR_DATOS_PROCESADOS: Path = RAIZ / 'data' / 'processed'
DIR_IMGS: Path = RAIZ / 'imgs'

ARCHIVO_PANEL: Path = DIR_DATOS_PROCESADOS / 'panel_completo.parquet'
ARCHIVO_MUESTRA: Path = DIR_DATOS_PROCESADOS / 'muestra.parquet'

# ---------------------------------------------------------------------------
# Fuentes: CSV de datos abiertos del MINEDUC, copiados a Google Drive
# ---------------------------------------------------------------------------
ANIOS: list[int] = [2026, 2025, 2024, 2023]

TABLAS: dict[str, str] = {
    'IP': 'Inscritos y puntajes',
    'SD': 'Socioeconómico',
    'PS': 'Postulantes y selección',
    'M': 'Matrícula',
}

IDS_DRIVE: dict[str, str] = {
    # A: Inscritos y puntajes
    'IP-2026': '1RurrECku8Ez_Rl3RlOfjP1SopxgpR6RC',
    'IP-2025': '1gAmWo_ujbhjJPr_vmWOhj-oXjycCk535',
    'IP-2024': '1gAx17O6USHw0AlXOsFSz9SFSG44TuUPY',
    'IP-2023': '1PcOS0fPcAMpwlunRqz9vJRHBwz1lTsLG',
    # B: Socioeconómico
    'SD-2026': '1qAV7_q6Z07lsJGgRxlb0W92vSeZmSm06',
    'SD-2025': '1b3QBKylAHGgw0CcXJHY3DfacDTHYUEAU',
    'SD-2024': '1xx6zZNFkAwUC4qwhVe8zpB6qHie8M6Se',
    'SD-2023': '15quWF_o5R4OO2caH9rF6hmy8dbExnXVH',
    # C: Postulantes y selección
    'PS-2026': '1F7cv0-gQLHbl2n7TvywUt9KedzVrr8fD',
    'PS-2025': '1DN-boiGtFXiL8_R9-c2j642ftp0fu25x',
    'PS-2024': '1TDi0q0l12_hGQTIC_f0X8zXGokq68tO1',
    'PS-2023': '188bcegEIs_quVaWDSQ0rc6zV4Q3kBJ96',
    # D: Matrícula
    'M-2026': '1oUQx9Sd-VFLRmhKoM_gFQMARY1AJS4yx',
    'M-2025': '1uuj7y793AXdgiFhy5GFpqkAF_tqVgEWH',
    'M-2024': '1aCClSoUgHLtBOIKbzpOXi29zj2L8cieS',
    'M-2023': '1IRDbdWaqWf-_mO7usfwdmkQ74iwuUmoi',
}
URL_DRIVE: str = ('https://drive.usercontent.google.com/download?id={}'
                  '&export=download&authuser=0&confirm=t')

# ---------------------------------------------------------------------------
# Decisión 2: postulaciones
# ---------------------------------------------------------------------------
# Códigos inferidos de los conteos: 24 (~160 mil por año, uno por estudiante)
# = seleccionado; 25 = lista de espera; 26 = preferencia eliminada por
# selección en una preferencia anterior. VERIFICAR con el libro de códigos.
ESTADO_SELECCIONADO: int = 24
ESTADO_LISTA_ESPERA: int = 25
ESTADOS_VALIDOS: set[int] = {ESTADO_SELECCIONADO, ESTADO_LISTA_ESPERA}

COL_PREFERENCIA: str = 'ORDEN_PREF'
COLUMNAS_PREF: set[str] = {
    'ORDEN_PREF', 'COD_CARRERA_PREF', 'ESTADO_PREF', 'TIPO_PREF',
    'PTJE_PREF', 'LUGAR_PREF',
}

# ---------------------------------------------------------------------------
# Decisión 4: tipos de datos
# ---------------------------------------------------------------------------
PRUEBAS: list[str] = ['CLEC', 'MATE1', 'MATE2', 'HCSOC', 'CIEN']
COLUMNAS_NUMERICAS: list[str] = [
    'RBD', 'SEXO', 'ANYO_DE_EGRESO', 'PROMEDIO_NOTAS', 'PTJE_NEM',
    'PTJE_RANKING', 'DEPENDENCIA', 'INGRESO_PERCAPITA_GRUPO_FA',
] + [
    f'{prueba}_{tipo}_{proceso}'
    for prueba in PRUEBAS
    for tipo in ('REG', 'INV')
    for proceso in ('ACTUAL', 'ANTERIOR')
]
CODIGO_NO_RESPONDE_INGRESO: int = 99

# ---------------------------------------------------------------------------
# Decisión 5: egreso reciente
# ---------------------------------------------------------------------------
# El proceso de admisión t se rinde a fines del año t-1, por lo que los
# egresados "del mismo año de rendición" tienen ANYO_DE_EGRESO = t - 1.
EGRESO_OFFSET: int = 1

# ---------------------------------------------------------------------------
# Muestra analítica y EDA
# ---------------------------------------------------------------------------
# 'regular': REG_ACTUAL y, si no rindió regular, INV_ACTUAL.
# 'cronologico': INV_ACTUAL (junio) si existe; si no, REG_ACTUAL.
CRITERIO_RENDICION: str = 'regular'
# Incluye a quienes rindieron Ciencias e Historia como grupo 'Ambas'.
INCLUIR_AMBAS: bool = True
ELECTIVAS: list[str] = ['Ciencias', 'Historia', 'Ambas']

PRUEBAS_PAES: dict[str, str] = {
    'CLEC': 'Comp. Lectora',
    'MATE1': 'Matemática 1',
    'MATE2': 'Matemática 2',
    'HCSOC': 'Historia y Cs. Sociales',
    'CIEN': 'Ciencias',
}

COLUMNAS_EDA: list[str] = [
    'MRUN', 'ANIO', 'RBD', 'DEPENDENCIA', 'RAMA_EDUCACIONAL', 'SEXO',
    'ANYO_DE_EGRESO', 'PROMEDIO_NOTAS', 'PTJE_NEM', 'PTJE_RANKING',
    'INGRESO_PERCAPITA_GRUPO_FA', 'postulo', 'postulacion_valida',
    'seleccionado', 'matriculado',
] + [f'{p}_{t}_ACTUAL' for p in PRUEBAS_PAES for t in ('REG', 'INV')]

# Columnas que el notebook 01 guarda para el EDA (incluye las del proceso
# anterior, usadas en el diagnóstico de "primera rendición").
COLUMNAS_PANEL: list[str] = COLUMNAS_EDA + ['egresado_reciente'] + [
    f'{p}_{t}_ANTERIOR' for p in PRUEBAS_PAES for t in ('REG', 'INV')
]

# Códigos de DEPENDENCIA (codificación MINEDUC). VERIFICAR con el diccionario.
DEPENDENCIA_ETIQUETAS: dict[int, str] = {
    1: 'Municipal',             # Corporación municipal
    2: 'Municipal',             # Municipal DAEM
    3: 'Part. subvencionado',
    4: 'Part. pagado',
    5: 'Adm. delegada',
    6: 'SLEP',                  # Servicio Local de Educación Pública
}
ORDEN_DEPENDENCIA: list[str] = [
    'Municipal', 'SLEP', 'Part. subvencionado', 'Adm. delegada',
    'Part. pagado', 'Sin dato',
]
SEXO_ETIQUETAS: dict[int, str] = {1: 'Hombre', 2: 'Mujer'}  # VERIFICAR
MODALIDAD_ETIQUETAS: dict[str, str] = {
    'H': 'Científico-humanista',
    'T': 'Técnico-profesional',
}
ORDEN_DECIL: list[str] = [str(d) for d in range(1, 11)] + ['No responde']

# RBD 99999 aparece como máximo en los 4 años: es un código, no un colegio.
# VERIFICAR en el diccionario (suele indicar exámenes libres o extranjero).
RBD_SIN_ESTABLECIMIENTO: int = 99999

# Tamaños mínimos para no graficar promedios con muy pocas observaciones.
MIN_N_CELDA: int = 30
MIN_ESTUDIANTES_COLEGIO: int = 10

# Guarda en imgs/ cada figura que se muestra con graficos.mostrar().
GUARDAR_FIGURAS: bool = True
