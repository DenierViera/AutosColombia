
import logging

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import UsuarioSistema
from app.services.auth import (
    AuthError,
    create_access_token,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=None)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    try:
        usuario = session.scalar(
            select(UsuarioSistema).where(
                UsuarioSistema.username == form_data.username
            )
        )

        if not usuario or not verify_password(
            form_data.password, usuario.password_hash
        ):
            raise AuthError(
                "Nombre de usuario o contraseña incorrectos."
            )

        if not usuario.activo:
            raise AuthError("La cuenta está desactivada.")

        token = create_access_token({
            "sub": str(usuario.id),
            "username": usuario.username,
            "rol": usuario.rol,
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "usuario": {
                "id": usuario.id,
                "username": usuario.username,
                "rol": usuario.rol,
            },
        }

    except AuthError:
        raise
    except Exception:
        logger.exception("ERROR INTERNO DURANTE LOGIN")
        raise
