"""Contrato de datos (bases, sección 7) + estructuras internas."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TipoAfirmacion = Literal["hecho", "declaracion", "inferencia", "hipotesis"]
EstadoEvidencia = Literal["insuficiente", "parcial", "suficiente_para_borrador"]
EstadoRevision = Literal["nuevo", "en_revision", "requiere_evidencia",
                         "aprobado_como_borrador", "descartado"]


class Noticia(BaseModel):
    id_noticia: str
    titulo: str
    url: str
    medio: str
    idioma: str | None = None
    fecha_publicacion: str | None = None   # ISO 8601 UTC; GDELT no la trae => null
    fecha_deteccion: str | None = None     # GDELT seendate
    fecha_extraccion: str
    tema: str | None = None
    origen: str                            # tvn_rss | gdelt | sintetico
    alcance_texto: str                     # titular | titular+descripcion | texto_completo
    descripcion: str | None = None         # opcional (RSS)


class Indicador(BaseModel):
    pais_iso3: str
    indicador_id: str
    anio: int
    valor: float | None                    # nulo se conserva, nunca 0
    unidad: str
    fuente_url: str
    fecha_extraccion: str
    licencia: str


class Sismo(BaseModel):
    id: str
    magnitude: float
    time: str
    updated: str | None = None
    longitude: float
    latitude: float
    depth: float | None = None
    place: str
    status: str | None = None
    url: str


class Cita(BaseModel):
    evidencia_id: str                      # id_noticia | ind:PAN:SL.UEM.TOTL.ZS:2024 | sismo id
    campo: str                             # titulo | descripcion | valor | magnitude ...
    pasaje: str | None = None


class Afirmacion(BaseModel):
    texto: str
    tipo: TipoAfirmacion
    citas: list[Cita] = Field(default_factory=list)


class Componentes(BaseModel):
    R: float = Field(ge=0, le=1)
    I: float = Field(ge=0, le=1)
    U: float = Field(ge=0, le=1)
    N: float = Field(ge=0, le=1)
    E: float = Field(ge=0, le=1)
    justificacion: dict[str, str] = Field(default_factory=dict)


class Borrador(BaseModel):
    titulo_propuesto: str
    enfoque_interes_publico: str
    brief: list[Afirmacion]                # <=250 palabras en total
    preguntas: list[str]                   # exactamente 3
    fuentes: list[str]
    verificaciones_pendientes: list[str]
    guion: list[Afirmacion]                # objetivo 45-60 s
    guion_segundos_estimados: int
    copy_digital: str                      # <=80 palabras
    aviso_alcance: str | None = None       # "Basado únicamente en titular/metadatos"
    generado_por: str = "plantilla"        # plantilla | ollama:<modelo> | anthropic:<modelo>


class Ficha(BaseModel):
    """Una línea de fichas.jsonl."""
    id_caso: str
    modalidad: str
    titulo: str
    tema: str
    ids_fuente: list[str]
    procedencias: dict[str, list[str]]     # procedencia -> ids de noticias
    fuentes_independientes: int
    que_se_reporta: str
    quien_lo_reporta: list[str]
    respaldado: list[Afirmacion]
    falta_comprobar: list[str]
    accion_recomendada: str
    contexto_oficial: list[dict]
    contradicciones: list[dict]
    alertas: list[str]                     # recirculada, contenido no confiable, solo titular...
    afirmaciones: list[Afirmacion]
    citas: list[Cita]
    puntaje: int
    banda: str
    componentes: Componentes
    version_reglas: str
    estado_evidencia: EstadoEvidencia
    borrador: Borrador | None
    estado_revision: EstadoRevision = "nuevo"
    revisor: str | None = None
    fecha_primera: str | None = None
    fecha_ultima: str | None = None
