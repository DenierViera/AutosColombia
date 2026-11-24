
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas.plan import (
    PlanCrear,
    PlanActualizar,
    PlanRespuesta,
)
from app.services import plan as service


router = APIRouter(prefix="/planes", tags=["Planes"])

DatabaseSession = Annotated[Session, Depends(get_session)]

PlanId = Annotated[
    int,
    Path(ge=1, le=9223372036854775807),
]


@router.post("", response_model=PlanRespuesta, status_code=201)
def crear(
    data: PlanCrear,
    session: DatabaseSession,
) -> PlanRespuesta:
    return service.create_plan(session, data)


@router.get("")
def listar(
    session: DatabaseSession,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return service.list_plans(session, offset, limit)


@router.get("/{plan_id}", response_model=PlanRespuesta)
def obtener(
    plan_id: PlanId,
    session: DatabaseSession,
) -> PlanRespuesta:
    return service.get_plan(session, plan_id)


@router.patch("/{plan_id}", response_model=PlanRespuesta)
def actualizar(
    plan_id: PlanId,
    data: PlanActualizar,
    session: DatabaseSession,
) -> PlanRespuesta:
    return service.update_plan(session, plan_id, data)


@router.patch("/{plan_id}/desactivar", response_model=PlanRespuesta)
def desactivar(
    plan_id: PlanId,
    session: DatabaseSession,
) -> PlanRespuesta:
    return service.deactivate_plan(session, plan_id)
