
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_engine
from app.models import Celda

celdas = [
    *[
        {"codigo": f"C-{i:02d}", "tipo": "Automovil"}
        for i in range(1, 71)
    ],
    *[
        {"codigo": f"M-{i:02d}", "tipo": "Moto"}
        for i in range(1, 11)
    ],
]

with Session(get_engine()) as db:
    existentes = set(db.scalars(select(Celda.codigo)).all())

    nuevas = [
        Celda(**celda)
        for celda in celdas
        if celda["codigo"] not in existentes
    ]

    try:
        db.add_all(nuevas)
        db.commit()

        print(f"Celdas nuevas registradas: {len(nuevas)}")
        print(f"Celdas que ya existían: {len(celdas) - len(nuevas)}")

    except Exception:
        db.rollback()
        raise
