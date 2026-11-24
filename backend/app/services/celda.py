
from functools import wraps

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Celda, Estancia, Suscripcion, Pago
from app.schemas.celda import CeldaActualizar, CeldaCrear


class CeldaError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def database_operation(operation):
    """Centraliza rollback y mensajes públicos sin detalles del driver."""
    @wraps(operation)
    def wrapped(session: Session, *args, **kwargs):
        try:
            return operation(session, *args, **kwargs)
        except IntegrityError as error:
            session.rollback()
            code = getattr(error.orig, "sqlstate", None)
            constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)

            if code == "23505" and constraint == "uq_celda_codigo":
                raise CeldaError(409, "Ya existe una celda con ese código.") from None

            if code == "23503":
                raise CeldaError(409, "La celda tiene registros relacionados y no se puede eliminar.") from None

            if code in {"23502", "23514"}:
                raise CeldaError(422, "Los datos incumplen las restricciones de la celda.") from None

            raise CeldaError(409, "La operación entra en conflicto con los datos existentes.") from None

        except SQLAlchemyError as error:
            session.rollback()
            print("ERROR SQLAlchemy:", repr(error))
            raise CeldaError(503, "No se pudo completar la operación con la base de datos.") from None

    return wrapped


def find_cell(session: Session, cell_id: int) -> Celda:
    cell = session.scalar(
        select(Celda).where(
            Celda.id == cell_id,
            Celda.eliminada.is_(False),
        )
    )

    if cell is None:
        raise CeldaError(404, "Celda no encontrada.")

    return cell


@database_operation
def create_cell(session: Session, data: CeldaCrear) -> Celda:
    cell = Celda(**data.model_dump())
    session.add(cell)
    session.commit()
    session.refresh(cell)
    return cell


@database_operation
def list_cells(session: Session, offset: int, limit: int) -> dict:
    ocupada = (
        select(Estancia.id)
        .where(
            Estancia.celda_id == Celda.id,
            Estancia.salida.is_(None),
        )
        .exists()
    )

    celdas_activas = Celda.eliminada.is_(False)

    reservada = (
        select(Suscripcion.id)
        .where(
            Suscripcion.celda_id == Celda.id,
            Suscripcion.estado == "ACTIVA",
            Suscripcion.fecha_inicio <= func.now(),
            Suscripcion.fecha_fin > func.now(),
            select(Pago.id)
            .where(Pago.suscripcion_id == Suscripcion.id)
            .exists(),
        )
        .exists()
    )

    total = session.scalar(
        select(func.count())
        .select_from(Celda)
        .where(celdas_activas)
    ) or 0

    ocupadas = session.scalar(
        select(func.count())
        .select_from(Celda)
        .where(celdas_activas, ocupada)
    ) or 0

    reservadas = session.scalar(
        select(func.count())
        .select_from(Celda)
        .where(celdas_activas, ~ocupada, reservada)
    ) or 0

    disponibles = total - ocupadas - reservadas
    items = list(
        session.execute(
            select(
                Celda,
                ocupada.label("ocupada"),
                reservada.label("reservada"),
            )
            .where(celdas_activas)
            .order_by(Celda.id)
            .offset(offset)
            .limit(limit)
        ).all()
    )

    celdas = [
        {
            "id": celda.id,
            "codigo": celda.codigo,
            "tipo": celda.tipo,
            "estado": (
                "Ocupada" if esta_ocupada
                else "Reservada" if esta_reservada
                else "Disponible"
            ),
        }
        for celda, esta_ocupada, esta_reservada in items
    ]

    return {
        "items": celdas,
        "total": total,
        "offset": offset,
        "limit": limit,
        "disponibles": disponibles,
        "ocupadas": ocupadas,
        "reservadas": reservadas,
    }


@database_operation
def list_available_cells(session: Session) -> list[Celda]:
    """Devuelve celdas activas sin vehículos ni suscripciones vigentes."""

    ocupada = (
        select(Estancia.id)
        .where(
            Estancia.celda_id == Celda.id,
            Estancia.salida.is_(None),
        )
        .exists()
    )

    reservada = (
        select(Suscripcion.id)
        .where(
            Suscripcion.celda_id == Celda.id,
            Suscripcion.estado == "ACTIVA",
            Suscripcion.fecha_fin > func.now(),
        )
        .exists()
    )

    return list(
        session.scalars(
            select(Celda)
            .where(
                Celda.eliminada.is_(False),
                ~ocupada,
                ~reservada,
            )
            .order_by(Celda.codigo)
        )
    )


@database_operation
def get_cell(session: Session, cell_id: int) -> Celda:
    return find_cell(session, cell_id)


@database_operation
def update_cell(session: Session, cell_id: int, data: CeldaActualizar) -> Celda:
    cell = find_cell(session, cell_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cell, key, value)

    session.commit()
    session.refresh(cell)
    return cell



@database_operation
def delete_cell(session: Session, cell_id: int) -> None:
    cell = session.scalar(
        select(Celda)
        .where(
            Celda.id == cell_id,
            Celda.eliminada.is_(False),
        )
        .with_for_update()
    )

    if cell is None:
        raise CeldaError(404, "Celda no encontrada.")

    tiene_estancia_abierta = session.scalar(
        select(Estancia.id)
        .where(
            Estancia.celda_id == cell.id,
            Estancia.salida.is_(None),
        )
        .limit(1)
    ) is not None

    if tiene_estancia_abierta:
        raise CeldaError(
            409,
            "No se puede eliminar la celda porque está ocupada por un vehículo.",
        )

    cell.eliminada = True
    session.commit()
