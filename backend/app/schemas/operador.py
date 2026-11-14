
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
)

from app.models import required_text


Texto = Annotated[
    str,
    BeforeValidator(lambda value: required_text(value, "El campo")),
]


class OperadorCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Texto
    telefono: Texto
    username: Texto
    password: str = Field(min_length=8)


class OperadorActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: Texto | None = None
    telefono: Texto | None = None
    username: Texto | None = None
    password: str | None = Field(default=None, min_length=8)

    @field_validator("*", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Los campos enviados no pueden ser nulos.")
        return value


class OperadorRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    nombre: str
    telefono: str
    username: str | None = None
    acceso_activo: bool


class OperadoresPagina(BaseModel):
    items: list[OperadorRespuesta]
    total: int
    offset: int
    limit: int


class AccesoActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activo: bool
