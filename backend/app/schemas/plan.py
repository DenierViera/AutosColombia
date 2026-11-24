from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


NombrePlan = Annotated[str, Field(min_length=1, max_length=150)]
DescripcionPlan = Annotated[str, Field(max_length=500)]


class PlanCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: NombrePlan
    descripcion: DescripcionPlan | None = None
    precio: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    duracion_dias: int = Field(gt=0)
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("El nombre del plan es obligatorio.")

        return value


class PlanActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: NombrePlan | None = None
    descripcion: DescripcionPlan | None = None
    precio: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )
    duracion_dias: int | None = Field(default=None, gt=0)
    activo: bool | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("El nombre del plan es obligatorio.")

        return value


class PlanRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    precio: Decimal
    duracion_dias: int
    activo: bool