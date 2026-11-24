
from datetime import datetime, timedelta, timezone
from functools import wraps

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Cliente, Celda, Estancia, Plan, Suscripcion
from app.schemas.suscripcion import SuscripcionCrear, SuscripcionRenovar


class SuscripcionError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def transaccion(operation):
    @wraps(operation)
    def wrapped(session: Session, *args, **kwargs):
        try:
            with session.begin():
                return operation(session, *args, **kwargs)

        except SuscripcionError:
            raise

        except IntegrityError as error:
            session.rollback()
            code = getattr(error.orig, "sqlstate", None)
            constraint = getattr(
                getattr(error.orig, "diag", None),
                "constraint_name",
                None,
            )

            if code == "23505":
                if constraint == "uq_suscripcion_celda_activa":
                    raise SuscripcionError(
                        409,
                        "La celda ya está reservada por otra suscripción.",
                    ) from None

                raise SuscripcionError(
                    409,
                    "La operación entra en conflicto con los datos existentes.",
                ) from None

            if code == "23503":
                raise SuscripcionError(
                    404,
                    "Uno de los registros relacionados no existe.",
                ) from None

            raise SuscripcionError(
                422,
                "Los datos incumplen las restricciones de la suscripción.",
            ) from None

        except SQLAlchemyError:
            session.rollback()
            raise SuscripcionError(
                503,
                "No se pudo completar la operación con la base de datos.",
            ) from None

    return wrapped


def actualizar_vencimientos(session: Session) -> None:
    ahora = datetime.now(timezone.utc)

    vencidas = session.scalars(
        select(Suscripcion)
        .where(
            Suscripcion.estado == "ACTIVA",
            Suscripcion.fecha_fin <= ahora,
        )
        .with_for_update()
    ).all()

    for suscripcion in vencidas:
        suscripcion.estado = "VENCIDA"


def buscar_suscripcion(
    session: Session,
    suscripcion_id: int,
) -> Suscripcion:
    suscripcion = session.scalar(
        select(Suscripcion)
        .where(Suscripcion.id == suscripcion_id)
        .with_for_update()
    )

    if suscripcion is None:
        raise SuscripcionError(404, "Suscripción no encontrada.")

    return suscripcion


@transaccion
def crear_suscripcion(
    session: Session,
    data: SuscripcionCrear,
) -> Suscripcion:
    actualizar_vencimientos(session)

    cliente = session.get(Cliente, data.cliente_id)
    if cliente is None:
        raise SuscripcionError(404, "Cliente no encontrado.")

    plan = session.get(Plan, data.plan_id)
    if plan is None or not plan.activo:
        raise SuscripcionError(404, "El plan no existe o está inactivo.")

    celda = session.scalar(
        select(Celda)
        .where(
            Celda.id == data.celda_id,
            Celda.eliminada.is_(False),
        )
        .with_for_update()
    )

    if celda is None:
        raise SuscripcionError(404, "Celda no encontrada.")

    suscripcion_existente = session.scalar(
        select(Suscripcion.id).where(
            Suscripcion.celda_id == celda.id,
            Suscripcion.estado == "ACTIVA",
        )
    )

    if suscripcion_existente is not None:
        raise SuscripcionError(
            409,
            "La celda ya está reservada por otra suscripción.",
        )

    estancia_abierta = session.scalar(
        select(Estancia.id).where(
            Estancia.celda_id == celda.id,
            Estancia.salida.is_(None),
        )
    )

    if estancia_abierta is not None:
        raise SuscripcionError(
            409,
            "No se puede reservar una celda que está ocupada.",
        )

    fecha_inicio = data.fecha_inicio or datetime.now(timezone.utc)

    if fecha_inicio.utcoffset() is None:
        raise SuscripcionError(
            422,
            "La fecha de inicio debe incluir zona horaria.",
        )

    suscripcion = Suscripcion(
        cliente_id=cliente.id,
        plan_id=plan.id,
        celda_id=celda.id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_inicio + timedelta(days=plan.duracion_dias),
        estado="ACTIVA",
    )

    session.add(suscripcion)
    session.flush()

    return suscripcion


@transaccion
def obtener_suscripcion(
    session: Session,
    suscripcion_id: int,
) -> Suscripcion:
    actualizar_vencimientos(session)
    return buscar_suscripcion(session, suscripcion_id)


@transaccion
def listar_suscripciones_cliente(
    session: Session,
    cliente_id: int,
) -> list[Suscripcion]:
    actualizar_vencimientos(session)

    cliente = session.get(Cliente, cliente_id)
    if cliente is None:
        raise SuscripcionError(404, "Cliente no encontrado.")

    return list(
        session.scalars(
            select(Suscripcion)
            .where(Suscripcion.cliente_id == cliente_id)
            .order_by(Suscripcion.fecha_inicio.desc())
        )
    )


@transaccion
def renovar_suscripcion(
    session: Session,
    suscripcion_id: int,
    data: SuscripcionRenovar,
) -> Suscripcion:
    actualizar_vencimientos(session)

    suscripcion = buscar_suscripcion(session, suscripcion_id)

    if suscripcion.estado == "CANCELADA":
        raise SuscripcionError(
            409,
            "No se puede renovar una suscripción cancelada.",
        )

    if suscripcion.fecha_fin.utcoffset() is None:
        raise SuscripcionError(
            422,
            "La fecha de vencimiento no tiene zona horaria.",
        )

    plan = session.get(Plan, data.plan_id)
    if plan is None or not plan.activo:
        raise SuscripcionError(404, "El plan no existe o está inactivo.")

    otra_suscripcion = session.scalar(
        select(Suscripcion.id).where(
            Suscripcion.celda_id == suscripcion.celda_id,
            Suscripcion.estado == "ACTIVA",
            Suscripcion.id != suscripcion.id,
        )
    )

    if otra_suscripcion is not None:
        raise SuscripcionError(
            409,
            "El cupo está asignado a otra suscripción.",
        )

    ahora = datetime.now(timezone.utc)

    nueva_fecha_inicio = max(ahora, suscripcion.fecha_fin)

    suscripcion.plan_id = plan.id
    suscripcion.fecha_inicio = nueva_fecha_inicio
    suscripcion.fecha_fin = nueva_fecha_inicio + timedelta(
        days=plan.duracion_dias
    )
    suscripcion.estado = "ACTIVA"

    session.flush()

    return suscripcion


@transaccion
def cancelar_suscripcion(
    session: Session,
    suscripcion_id: int,
) -> Suscripcion:
    actualizar_vencimientos(session)

    suscripcion = buscar_suscripcion(session, suscripcion_id)

    if suscripcion.estado == "CANCELADA":
        raise SuscripcionError(
            409,
            "La suscripción ya está cancelada.",
        )

    suscripcion.estado = "CANCELADA"
    session.flush()

    return suscripcion
