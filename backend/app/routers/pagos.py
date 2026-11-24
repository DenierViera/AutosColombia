
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.pago import (
    PagoCrear,
    PagoRespuesta,
    ContratacionPagoCrear,
    ContratacionPagoRespuesta,
)
from app.services.pago import ServicioPago


router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
)

DatabaseSession = Annotated[Session, Depends(get_session)]

SuscripcionId = Annotated[
    int,
    Path(ge=1, le=9223372036854775807),
]


@router.post(
    "",
    response_model=PagoRespuesta,
    status_code=201,
)
def registrar(
    data: PagoCrear,
    session: DatabaseSession,
) -> PagoRespuesta:
    return ServicioPago(session).registrar_pago(data)


@router.post(
    "/contratar",
    response_model=ContratacionPagoRespuesta,
    status_code=201,
)
def contratar(
    data: ContratacionPagoCrear,
    session: DatabaseSession,
) -> ContratacionPagoRespuesta:
    return ServicioPago(session).contratar_con_pago(data)


@router.get(
    "",
    response_model=list[PagoRespuesta],
)
def listar(
    session: DatabaseSession,
) -> list[PagoRespuesta]:
    return ServicioPago(session).listar_todos()


@router.get(
    "/suscripcion/{suscripcion_id}",
    response_model=list[PagoRespuesta],
)
def listar_por_suscripcion(
    suscripcion_id: SuscripcionId,
    session: DatabaseSession,
) -> list[PagoRespuesta]:
    return ServicioPago(session).listar_pagos_suscripcion(
        suscripcion_id
    )
