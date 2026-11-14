from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers.vehiculos import router as vehiculos_router
from app.services.vehiculo import VehiculoError
from app.routers.celdas import router as celdas_router
from app.services.celda import CeldaError
from app.routers.operadores import router as operadores_router
from app.services.operador import OperadorError
from app.routers.estancias import router as estancias_router
from app.services.estancia import EstanciaError
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router
from app.services.auth import AuthError

app = FastAPI(title="Autos Colombia API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:4200",
        "http://localhost:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(vehiculos_router)
app.include_router(celdas_router)
app.include_router(operadores_router)
app.include_router(estancias_router)
app.include_router(auth_router)


@app.exception_handler(VehiculoError)
@app.exception_handler(CeldaError)
@app.exception_handler(OperadorError)
@app.exception_handler(EstanciaError)
async def entity_error_handler(request, error: VehiculoError | CeldaError | OperadorError | EstanciaError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.exception_handler(AuthError)
async def auth_error_handler(request, error: AuthError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"detail": error.detail},
    )