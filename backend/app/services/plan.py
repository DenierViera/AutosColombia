
from functools import wraps

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Plan
from app.schemas.plan import PlanCrear, PlanActualizar


class PlanError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def database_operation(operation):
    @wraps(operation)
    def wrapped(session: Session, *args, **kwargs):
        try:
            return operation(session, *args, **kwargs)

        except IntegrityError as error:
            session.rollback()
            code = getattr(error.orig, "sqlstate", None)

            if code == "23505":
                raise PlanError(
                    409,
                    "Ya existe un plan con ese nombre.",
                ) from None

            raise PlanError(
                409,
                "La operación entra en conflicto con los datos existentes.",
            ) from None

        except SQLAlchemyError:
            session.rollback()
            raise PlanError(
                503,
                "No se pudo completar la operación con la base de datos.",
            ) from None

    return wrapped


def find_plan(session: Session, plan_id: int) -> Plan:
    plan = session.get(Plan, plan_id)

    if plan is None:
        raise PlanError(404, "Plan no encontrado.")

    return plan


@database_operation
def create_plan(session: Session, data: PlanCrear) -> Plan:
    plan = Plan(**data.model_dump())

    session.add(plan)
    session.commit()
    session.refresh(plan)

    return plan


@database_operation
def list_plans(
    session: Session,
    offset: int,
    limit: int,
) -> dict:
    total = session.scalar(
        select(func.count()).select_from(Plan)
    ) or 0

    items = list(
        session.scalars(
            select(Plan)
            .order_by(Plan.id)
            .offset(offset)
            .limit(limit)
        )
    )

    return {
        "items": items,
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@database_operation
def get_plan(session: Session, plan_id: int) -> Plan:
    return find_plan(session, plan_id)


@database_operation
def update_plan(
    session: Session,
    plan_id: int,
    data: PlanActualizar,
) -> Plan:
    plan = find_plan(session, plan_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)

    session.commit()
    session.refresh(plan)

    return plan


@database_operation
def deactivate_plan(session: Session, plan_id: int) -> Plan:
    plan = find_plan(session, plan_id)

    plan.activo = False

    session.commit()
    session.refresh(plan)

    return plan
