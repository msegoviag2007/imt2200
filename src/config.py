"""Rutas, fuentes de datos y constantes compartidas por los notebooks."""
from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------
RAIZ: Path = Path(__file__).resolve().parents[1]
DIR_DATOS_PROCESADOS: Path = RAIZ / 'data' / 'processed'
DIR_IMGS: Path = RAIZ / 'imgs'
ARCHIVO_PANEL: Path = DIR_DATOS_PROCESADOS / 'panel_completo.parquet'
ARCHIVO_MUESTRA: Path = DIR_DATOS_PROCESADOS / 'muestra.parquet'

# ---------------------------------------------------------------------------
# Fuentes: CSV de datos abiertos del MINEDUC en Google Drive (se leen directo
# desde ahí, sin guardar copias locales)
# ---------------------------------------------------------------------------
ANIOS: list[int] = [2026, 2025, 2024, 2023]

TABLAS: dict[str, str] = {
    'IP': 'Inscritos y puntajes',
    'SD': 'Socioeconómico',
    'PS': 'Postulantes y selección',
    'M': 'Matrícula',
}

IDS_DRIVE: dict[str, str] = {
    'IP-2026': '1RurrECku8Ez_Rl3RlOfjP1SopxgpR6RC',
    'IP-2025': '1gAmWo_ujbhjJPr_vmWOhj-oXjycCk535',
    'IP-2024': '1gAx17O6USHw0AlXOsFSz9SFSG44TuUPY',
    'IP-2023': '1PcOS0fPcAMpwlunRqz9vJRHBwz1lTsLG',
    'SD-2026': '1qAV7_q6Z07lsJGgRxlb0W92vSeZmSm06',
    'SD-2025': '1b3QBKylAHGgw0CcXJHY3DfacDTHYUEAU',
    'SD-2024': '1xx6zZNFkAwUC4qwhVe8zpB6qHie8M6Se',
    'SD-2023': '15quWF_o5R4OO2caH9rF6hmy8dbExnXVH',
    'PS-2026': '1F7cv0-gQLHbl2n7TvywUt9KedzVrr8fD',
    'PS-2025': '1DN-boiGtFXiL8_R9-c2j642ftp0fu25x',
    'PS-2024': '1TDi0q0l12_hGQTIC_f0X8zXGokq68tO1',
    'PS-2023': '188bcegEIs_quVaWDSQ0rc6zV4Q3kBJ96',
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
# Códigos de ESTADO_PREF según el libro de códigos de Postulación 2026
# (docs/libro_codigos_postulacion_2026.pdf, Anexo I): 24 = en lista de
# seleccionados; 25 = en lista de espera; 26 = seleccionado en una
# preferencia anterior. El resto son causales de postulación no válida.
# Seleccionado: algún estado 24 o 26 (en PS-2023 a veces falta el 24).
ESTADOS_SELECCION: set[int] = {24, 26}
# Postulación válida (como la "P" de SITUACION_POSTULANTE).
ESTADOS_VALIDOS: set[int] = {24, 25, 26}

# PS-2023 viene en formato ancho: para cada preferencia n (01 a 20) trae las
# columnas COD_CARRERA_PREF_n, ESTADO_PREF_n, PTJE_PREF_n y LUGAR_PREF_n.
N_PREFERENCIAS_ANCHO: int = 20
COLUMNAS_PREF_ANCHO: list[str] = [
    'COD_CARRERA_PREF', 'ESTADO_PREF', 'PTJE_PREF', 'LUGAR_PREF',
]

# ---------------------------------------------------------------------------
# Decisión 4: tipos de datos (columnas que se fuerzan a número)
# ---------------------------------------------------------------------------
PRUEBAS_PAES: dict[str, str] = {
    'CLEC': 'Comp. Lectora',
    'MATE1': 'Matemática 1',
    'HCSOC': 'Historia y Cs. Sociales',
    'CIEN': 'Ciencias',
}
COLUMNAS_PUNTAJES: list[str] = [
    'CLEC_REG_ACTUAL', 'CLEC_INV_ACTUAL', 'CLEC_REG_ANTERIOR',
    'CLEC_INV_ANTERIOR', 'MATE1_REG_ACTUAL', 'MATE1_INV_ACTUAL',
    'MATE1_REG_ANTERIOR', 'MATE1_INV_ANTERIOR', 'HCSOC_REG_ACTUAL',
    'HCSOC_INV_ACTUAL', 'HCSOC_REG_ANTERIOR', 'HCSOC_INV_ANTERIOR',
    'CIEN_REG_ACTUAL', 'CIEN_INV_ACTUAL', 'CIEN_REG_ANTERIOR',
    'CIEN_INV_ANTERIOR',
]
COLUMNAS_NUMERICAS: list[str] = [
    'RBD', 'CODIGO_ENS', 'DEPENDENCIA', 'SEXO', 'ANYO_DE_EGRESO',
    'PROMEDIO_NOTAS', 'PTJE_NEM', 'INGRESO_PERCAPITA_GRUPO_FA',
] + COLUMNAS_PUNTAJES
CODIGO_NO_RESPONDE_INGRESO: int = 99

# Columnas que el notebook 01 guarda en el panel para el EDA.
COLUMNAS_PANEL: list[str] = [
    'MRUN', 'ANIO', 'RBD', 'CODIGO_ENS', 'DEPENDENCIA', 'RAMA_EDUCACIONAL',
    'SEXO', 'ANYO_DE_EGRESO', 'PROMEDIO_NOTAS', 'PTJE_NEM',
    'INGRESO_PERCAPITA_GRUPO_FA', 'postulo', 'postulacion_valida',
    'seleccionado', 'ptje_ponderado_max', 'matriculado',
] + COLUMNAS_PUNTAJES

# ---------------------------------------------------------------------------
# Muestra analítica
# ---------------------------------------------------------------------------
# El proceso de admisión t se rinde a fines del año t - 1: los egresados
# "del año de rendición" tienen ANYO_DE_EGRESO = ANIO - 1.
EGRESO_OFFSET: int = 1
ELECTIVAS: list[str] = ['Ciencias', 'Historia', 'Ambas']

# Códigos de enseñanza media para niños y jóvenes (libro de códigos de
# Inscritos 2026, Anexo II). Los demás (x60 a x63 y 963) son educación de
# adultos; quienes validan o reconocen estudios (H3, H4) no traen código.
CODIGOS_ENS_REGULAR: list[int] = [310, 410, 510, 610, 710, 810, 910]
# RBD 99999: código no documentado en los libros de códigos (no es un
# colegio); se excluye con el filtro de educación regular.
RBD_SIN_ESTABLECIMIENTO: int = 99999

# Columnas que el notebook 02 guarda en muestra.parquet para el modelamiento.
COLUMNAS_MUESTRA: list[str] = [
    'MRUN', 'ANIO', 'RBD', 'dependencia', 'decil', 'decil_num', 'sexo',
    'modalidad', 'electiva', 'PROMEDIO_NOTAS', 'PTJE_NEM', 'PAES_electiva',
    'CLEC_1ra', 'MATE1_1ra', 'NEM_z', 'PAES_z', 'brecha', 'brecha_cond',
    'brecha_CLEC', 'brecha_MATE1', 'postulo', 'postulacion_valida',
    'seleccionado', 'matriculado', 'ptje_ponderado_max',
]

# ---------------------------------------------------------------------------
# Etiquetas (libro de códigos de Inscritos 2026, sección 1.2)
# ---------------------------------------------------------------------------
DEPENDENCIA_ETIQUETAS: dict[int, str] = {
    1: 'Municipal',             # Corporación Municipal
    2: 'Municipal',             # Municipal
    3: 'Part. subvencionado',   # Particular Subvencionado
    4: 'Part. pagado',          # Particular Pagado
    5: 'Adm. delegada',         # Corp. de Administración Delegada
    6: 'SLEP',                  # Servicio Local de Educación (SLE)
}
ORDEN_DEPENDENCIA: list[str] = [
    'Municipal', 'SLEP', 'Part. subvencionado', 'Adm. delegada',
    'Part. pagado',
]
# Dependencias que se grafican como líneas (Adm. delegada tiene pocos casos).
DEPENDENCIAS_LINEAS: list[str] = [
    'Municipal', 'SLEP', 'Part. subvencionado', 'Part. pagado',
]
SEXO_ETIQUETAS: dict[int, str] = {1: 'Hombre', 2: 'Mujer'}
MODALIDAD_ETIQUETAS: dict[str, str] = {
    'H': 'Científico-humanista',
    'T': 'Técnico-profesional',
}
ORDEN_DECIL: list[str] = [str(d) for d in range(1, 11)] + ['No responde']

# Tamaños mínimos para no mostrar promedios con muy pocas observaciones.
MIN_N_CELDA: int = 30
MIN_ESTUDIANTES_COLEGIO: int = 10
