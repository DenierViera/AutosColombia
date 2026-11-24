from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.suscripcion import SuscripcionRespuesta

class PagoCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suscripcion_id: int = Field(gt=0)
    valor: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    metodo_pago: str = Field(min_length=1, max_length=100)
    referencia: str | None = Field(default=None, max_length=255)

    @field_validator("metodo_pago")
    @classmethod
    def validar_metodo_pago(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("El método de pago es obligatorio.")

        return value


class ContratacionPagoCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identificacion: str = Field(min_length=1, max_length=50)
    plan_id: int = Field(gt=0)
    celda_id: int = Field(gt=0)

    valor: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )

    metodo_pago: str = Field(min_length=1, max_length=100)
    referencia: str | None = Field(default=None, max_length=255)

    @field_validator("identificacion", "metodo_pago")
    @classmethod
    def validar_textos(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Este campo es obligatorio.")

        return value


class RenovacionPagoCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: int = Field(gt=0)
    valor: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    metodo_pago: str = Field(min_length=1, max_length=100)
    referencia: str | None = Field(default=None, max_length=255)

    @field_validator("metodo_pago")
    @classmethod
    def validar_metodo_pago(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El método de pago es obligatorio.")
        return value

class PagoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suscripcion_id: int
    valor: Decimal
    fecha_pago: datetime
    metodo_pago: str
    referencia: str | None = None


class ContratacionPagoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suscripcion: SuscripcionRespuesta
    pago: PagoRespuesta
