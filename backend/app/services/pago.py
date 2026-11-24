
from datetime import datetime, timezone, timedelta
from functools import wraps

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import (
    Cliente,
    Celda,
    Estancia,
    Pago,
    Plan,
    Suscripcion,
)
from app.schemas.pago import (
    PagoCrear,
    ContratacionPagoCrear,
    RenovacionPagoCrear,
)
from app.schemas.pago import PagoCrear, ContratacionPagoCrear


class PagoError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


def transaccion(operation):
    @wraps(operation)
    def wrapped(self, *args, **kwargs):
        try:
            with self.session.begin():
                return operation(self, *args, **kwargs)

        except PagoError:
            raise

        except IntegrityError as error:
            self.session.rollback()
            code = getattr(error.orig, "sqlstate", None)
            constraint = getattr(
                getattr(error.orig, "diag", None),
                "constraint_name",
                None,
            )

            if code == "23503":
                raise PagoError(
                    404,
                    "Uno de los registros relacionados no existe.",
                ) from None

            if code == "23505":
                if constraint == "uq_suscripcion_celda_activa":
                    raise PagoError(
                        409,
                        "La celda ya está reservada por otra suscripción.",
                    ) from None

                raise PagoError(
                    409,
                    "La operación entra en conflicto con los datos existentes.",
                ) from None

            if code in {"23502", "23514"}:
                raise PagoError(
                    422,
                    "Los datos incumplen las restricciones de la base de datos.",
                ) from None

            raise PagoError(
                409,
                "No se pudo completar la operación por un conflicto.",
            ) from None

        except SQLAlchemyError:
            self.session.rollback()
            raise PagoError(
                503,
                "No se pudo completar la operación con la base de datos.",
            ) from None

    return wrapped


class ServicioPago:
    def __init__(self, session: Session) -> None:
        self.session = session

    @transaccion
    def contratar_con_pago(
        self,
        data: ContratacionPagoCrear,
    ) -> dict:
        # 1. Buscar al propietario mediante su identificación.
        cliente = self.session.scalar(
            select(Cliente)
            .where(Cliente.identificacion == data.identificacion)
            .with_for_update()
        )

        if cliente is None:
            raise PagoError(
                404,
                "No existe un propietario registrado con esa identificación. Regístrelo primero.",
            )

        # 2. Verificar que el plan exista y esté activo.
        plan = self.session.get(Plan, data.plan_id)

        if plan is None or not plan.activo:
            raise PagoError(
                404,
                "El plan no existe o está inactivo.",
            )

        # 3. Verificar el valor recibido.
        if data.valor != plan.precio:
            raise PagoError(
                422,
                "El valor del pago debe coincidir con el precio del plan.",
            )

        # 4. Bloquear y verificar la celda.
        celda = self.session.scalar(
            select(Celda)
            .where(
                Celda.id == data.celda_id,
                Celda.eliminada.is_(False),
            )
            .with_for_update()
        )

        if celda is None:
            raise PagoError(404, "La celda no existe o está eliminada.")

        # 5. Actualizar vencimientos antes de comprobar disponibilidad.
        ahora = datetime.now(timezone.utc)

        vencidas = self.session.scalars(
            select(Suscripcion)
            .where(
                Suscripcion.estado == "ACTIVA",
                Suscripcion.fecha_fin <= ahora,
            )
            .with_for_update()
        ).all()

        for suscripcion_vencida in vencidas:
            suscripcion_vencida.estado = "VENCIDA"

        # 6. Comprobar que la celda no tenga otra suscripción activa.
        suscripcion_existente = self.session.scalar(
            select(Suscripcion.id).where(
                Suscripcion.celda_id == celda.id,
                Suscripcion.estado == "ACTIVA",
            )
        )

        if suscripcion_existente is not None:
            raise PagoError(
                409,
                "La celda ya está reservada por otra suscripción.",
            )

        # 7. Comprobar que no haya un vehículo ocupando la celda.
        estancia_abierta = self.session.scalar(
            select(Estancia.id).where(
                Estancia.celda_id == celda.id,
                Estancia.salida.is_(None),
            )
        )

        if estancia_abierta is not None:
            raise PagoError(
                409,
                "No se puede asignar una celda que está ocupada.",
            )

        # 8. Crear la suscripción.
        suscripcion = Suscripcion(
            cliente_id=cliente.id,
            plan_id=plan.id,
            celda_id=celda.id,
            fecha_inicio=ahora,
            fecha_fin=ahora + timedelta(days=plan.duracion_dias),
            estado="ACTIVA",
        )

        self.session.add(suscripcion)
        self.session.flush()

        # 9. Registrar el pago asociado a la nueva suscripción.
        pago = Pago(
            suscripcion_id=suscripcion.id,
            valor=data.valor,
            metodo_pago=data.metodo_pago,
            referencia=data.referencia,
        )

        self.session.add(pago)
        self.session.flush()

        return {
            "suscripcion": suscripcion,
            "pago": pago,
        }


    @transaccion
    def renovar_con_pago(
        self,
        suscripcion_id: int,
        data: RenovacionPagoCrear,
    ) -> dict:
        # 1. Buscar y bloquear la suscripción.
        suscripcion = self.session.scalar(
            select(Suscripcion)
            .where(Suscripcion.id == suscripcion_id)
            .with_for_update()
        )

        if suscripcion is None:
            raise PagoError(404, "Suscripción no encontrada.")

        if suscripcion.estado == "CANCELADA":
            raise PagoError(
                409,
                "No se puede renovar una suscripción cancelada.",
            )

        # 2. Actualizar vencimientos.
        ahora = datetime.now(timezone.utc)

        vencidas = self.session.scalars(
            select(Suscripcion)
            .where(
                Suscripcion.estado == "ACTIVA",
                Suscripcion.fecha_fin <= ahora,
            )
            .with_for_update()
        ).all()

        for item in vencidas:
            item.estado = "VENCIDA"

        # 3. Verificar el plan.
        plan = self.session.get(Plan, data.plan_id)

        if plan is None or not plan.activo:
            raise PagoError(404, "El plan no existe o está inactivo.")

        if data.valor != plan.precio:
            raise PagoError(
                422,
                "El valor del pago debe coincidir con el precio del plan.",
            )

        # 4. Comprobar que el cupo no esté asignado a otra suscripción.
        otra_suscripcion = self.session.scalar(
            select(Suscripcion.id).where(
                Suscripcion.celda_id == suscripcion.celda_id,
                Suscripcion.estado == "ACTIVA",
                Suscripcion.id != suscripcion.id,
            )
        )

        if otra_suscripcion is not None:
            raise PagoError(
                409,
                "El cupo ya está asignado a otra suscripción.",
            )

        # 5. Calcular el nuevo periodo.
        fecha_inicio = max(ahora, suscripcion.fecha_fin)

        suscripcion.plan_id = plan.id
        suscripcion.fecha_inicio = fecha_inicio
        suscripcion.fecha_fin = (
            fecha_inicio + timedelta(days=plan.duracion_dias)
        )
        suscripcion.estado = "ACTIVA"

        self.session.flush()

        # 6. Registrar el pago.
        pago = Pago(
            suscripcion_id=suscripcion.id,
            valor=data.valor,
            metodo_pago=data.metodo_pago,
            referencia=data.referencia,
        )

        self.session.add(pago)
        self.session.flush()

        return {
            "suscripcion": suscripcion,
            "pago": pago,
        }

    @transaccion
    def registrar_pago(self, data: PagoCrear) -> Pago:
        suscripcion = self.session.get(
            Suscripcion,
            data.suscripcion_id,
        )

        if suscripcion is None:
            raise PagoError(404, "Suscripción no encontrada.")

        pago = Pago(**data.model_dump())

        self.session.add(pago)
        self.session.flush()

        return pago

    @transaccion
    def listar_pagos_suscripcion(
        self,
        suscripcion_id: int,
    ) -> list[Pago]:
        suscripcion = self.session.get(
            Suscripcion,
            suscripcion_id,
        )

        if suscripcion is None:
            raise PagoError(404, "Suscripción no encontrada.")

        return list(
            self.session.scalars(
                select(Pago)
                .where(Pago.suscripcion_id == suscripcion_id)
                .order_by(Pago.fecha_pago.desc())
            )
        )

    @transaccion
    def listar_todos(self) -> list[Pago]:
        return list(
            self.session.scalars(
                select(Pago)
                .order_by(Pago.fecha_pago.desc())
            )
        )
