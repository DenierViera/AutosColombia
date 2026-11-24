
from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.suscripcion import SuscripcionRespuesta
from app.schemas.pago import (
    RenovacionPagoCrear,
    ContratacionPagoRespuesta,
)
from app.services import suscripcion as service
from app.services.pago import ServicioPago


router = APIRouter(
    prefix="/suscripciones",
    tags=["Suscripciones"],
)

DatabaseSession = Annotated[Session, Depends(get_session)]

SuscripcionId = Annotated[
    int,
    Path(ge=1, le=9223372036854775807),
]

ClienteId = Annotated[
    int,
    Path(ge=1, le=9223372036854775807),
]


@router.get(
    "/cliente/{cliente_id}",
    response_model=list[SuscripcionRespuesta],
)
def listar_por_cliente(
    cliente_id: ClienteId,
    session: DatabaseSession,
):
    return service.listar_suscripciones_cliente(
        session,
        cliente_id,
    )


@router.get(
    "/{suscripcion_id}",
    response_model=SuscripcionRespuesta,
)
def obtener(
    suscripcion_id: SuscripcionId,
    session: DatabaseSession,
):
    return service.obtener_suscripcion(
        session,
        suscripcion_id,
    )


@router.post(
    "/{suscripcion_id}/renovar",
    response_model=ContratacionPagoRespuesta,
)
def renovar(
    suscripcion_id: SuscripcionId,
    data: RenovacionPagoCrear,
    session: DatabaseSession,
):
    return ServicioPago(session).renovar_con_pago(
        suscripcion_id,
        data,
    )


@router.post(
    "/{suscripcion_id}/cancelar",
    response_model=SuscripcionRespuesta,
)
def cancelar(
    suscripcion_id: SuscripcionId,
    session: DatabaseSession,
):
    return service.cancelar_suscripcion(
        session,
        suscripcion_id,
    )
