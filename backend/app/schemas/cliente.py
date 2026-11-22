from typing import Annotated
from app.schemas.vehiculo import VehiculoRespuesta

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
)

from app.models import required_text


TextoCliente = Annotated[
    str,
    BeforeValidator(lambda value: required_text(value, "El campo")),
]


Identificacion = Annotated[
    TextoCliente,
    AfterValidator(str.strip),
]


class ClienteCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identificacion: Identificacion
    nombre_completo: TextoCliente
    telefono: TextoCliente


class ClienteActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identificacion: Identificacion | None = None
    nombre_completo: TextoCliente | None = None
    telefono: TextoCliente | None = None

    @field_validator("*", mode="before")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("Los campos enviados no pueden ser nulos.")
        return value


class ClienteRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    identificacion: str
    nombre_completo: str
    telefono: str

class ClienteDetalle(ClienteRespuesta):
    vehiculos: list[VehiculoRespuesta] = Field(default_factory=list)

class ClientesPagina(BaseModel):
    items: list[ClienteRespuesta]
    total: int
    offset: int
    limit: int