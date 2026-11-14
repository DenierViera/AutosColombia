
from functools import wraps

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Operador, UsuarioSistema
from app.schemas.operador import OperadorActualizar, OperadorCrear
from app.services.auth import hash_password


class OperadorError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def database_operation(operation):
    """Centraliza rollback y mensajes públicos sin detalles del driver."""
    @wraps(operation)
    def wrapped(session: Session, *args, **kwargs):
        try:
            return operation(session, *args, **kwargs)
        except OperadorError:
            session.rollback()
            raise
        except IntegrityError as error:
            session.rollback()
            code = getattr(error.orig, "sqlstate", None)

            if code == "23503":
                raise OperadorError(
                    409,
                    "El operador tiene registros relacionados y no se puede eliminar."
                ) from None

            if code in {"23502", "23514"}:
                raise OperadorError(
                    422,
                    "Los datos incumplen las restricciones del operador."
                ) from None

            raise OperadorError(
                409,
                "El usuario o los datos ya existen."
            ) from None

        except SQLAlchemyError:
            session.rollback()
            raise OperadorError(
                503,
                "No se pudo completar la operación con la base de datos."
            ) from None

    return wrapped


def find_operator(session: Session, operator_id: int) -> Operador:
    operator = session.get(Operador, operator_id)

    if operator is None:
        raise OperadorError(404, "Operador no encontrado.")

    return operator


def find_account(session: Session, operator_id: int):
    return session.scalar(
        select(UsuarioSistema).where(
            UsuarioSistema.operador_id == operator_id
        )
    )


def operator_response(session: Session, operator: Operador) -> dict:
    account = find_account(session, operator.id)

    return {
        "id": operator.id,
        "nombre": operator.nombre,
        "telefono": operator.telefono,
        "username": account.username if account else None,
        "acceso_activo": bool(account and account.activo),
    }


@database_operation
def create_operator(session: Session, data: OperadorCrear) -> dict:
    operator = Operador(
        nombre=data.nombre,
        telefono=data.telefono,
    )

    session.add(operator)
    session.flush()

    account = UsuarioSistema(
        operador_id=operator.id,
        username=data.username,
        password_hash=hash_password(data.password),
        rol="OPERADOR",
        activo=True,
    )

    session.add(account)
    session.commit()
    session.refresh(operator)

    return operator_response(session, operator)


@database_operation
def list_operators(session: Session, offset: int, limit: int) -> dict:
    total = session.scalar(
        select(func.count()).select_from(Operador)
    ) or 0

    operators = list(
        session.scalars(
            select(Operador)
            .order_by(Operador.id)
            .offset(offset)
            .limit(limit)
        )
    )

    return {
        "items": [
            operator_response(session, operator)
            for operator in operators
        ],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@database_operation
def get_operator(session: Session, operator_id: int) -> dict:
    operator = find_operator(session, operator_id)
    return operator_response(session, operator)


@database_operation
def update_operator(
    session: Session,
    operator_id: int,
    data: OperadorActualizar,
) -> dict:
    operator = find_operator(session, operator_id)
    account = find_account(session, operator_id)

    changes = data.model_dump(exclude_unset=True)

    username = changes.pop("username", None)
    password = changes.pop("password", None)

    for key, value in changes.items():
        setattr(operator, key, value)

    if account is None:
        if username is not None and password is not None:
            account = UsuarioSistema(
                operador_id=operator.id,
                username=username,
                password_hash=hash_password(password),
                rol="OPERADOR",
                activo=True,
            )
            session.add(account)
        elif username is not None or password is not None:
            raise OperadorError(
                422,
                "Para crear las credenciales debes indicar usuario y contraseña."
            )
    else:
        if username is not None:
            account.username = username

        if password is not None:
            account.password_hash = hash_password(password)

    session.commit()
    session.refresh(operator)

    return operator_response(session, operator)


@database_operation
def update_operator_access(
    session: Session,
    operator_id: int,
    active: bool,
) -> dict:
    operator = find_operator(session, operator_id)
    account = find_account(session, operator_id)

    if account is None:
        raise OperadorError(
            404,
            "Este operador todavía no tiene credenciales de acceso."
        )

    account.activo = active

    session.commit()
    session.refresh(operator)

    return operator_response(session, operator)


@database_operation
def delete_operator(session: Session, operator_id: int) -> None:
    operator = find_operator(session, operator_id)
    account = find_account(session, operator_id)

    if account is not None:
        session.delete(account)

    session.delete(operator)
    session.commit()
