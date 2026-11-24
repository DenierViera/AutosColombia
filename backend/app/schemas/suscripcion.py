from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SuscripcionCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cliente_id: int = Field(gt=0)
    plan_id: int = Field(gt=0)
    celda_id: int = Field(gt=0)
    fecha_inicio: datetime | None = None


class SuscripcionRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    plan_id: int
    celda_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str


class SuscripcionRenovar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: int = Field(gt=0)


class SuscripcionDetalle(SuscripcionRespuesta):
    nombre_plan: str
    precio: Decimal
    nombre_cliente: str
    codigo_celda: str