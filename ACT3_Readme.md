# AutosColombia

Sistema web para administrar la operación de un parqueadero: propietarios, vehículos, celdas, operadores, entradas y salidas, planes, suscripciones y pagos.

## 1. Tecnologías

- **Frontend:** Angular 22, TypeScript, formularios reactivos y RxJS.
- **Backend:** Python, FastAPI, SQLAlchemy y Pydantic.
- **Base de datos:** PostgreSQL.
- **Migraciones:** Alembic.
- **Autenticación:** tokens JWT y contraseñas almacenadas como hash.

## 2. Arquitectura general

El proyecto está separado en dos aplicaciones:

```text
AutosColombia/
├── backend/
│   ├── app/
│   │   ├── routers/       # Rutas HTTP de la API
│   │   ├── schemas/       # Validación y estructura de datos
│   │   ├── services/      # Reglas de negocio y transacciones
│   │   ├── models.py      # Modelos y relaciones de PostgreSQL
│   │   ├── database.py   # Conexión y sesiones de base de datos
│   │   └── main.py       # Inicialización de FastAPI
│   ├── migrations/       # Versiones del esquema de base de datos
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/app/
    │   ├── auth/          # Inicio de sesión
    │   ├── control-acceso/
    │   ├── clientes/
    │   ├── vehiculos/
    │   ├── celdas/
    │   ├── operadores/
    │   ├── pagos/
    │   ├── services/      # Comunicación HTTP con la API
    │   └── models/        # Tipos de datos TypeScript
    └── package.json
```

El frontend presenta los formularios y las vistas. Los servicios Angular envían solicitudes HTTP al backend. FastAPI recibe las solicitudes, valida los datos mediante los esquemas, ejecuta las reglas de negocio y consulta o modifica PostgreSQL mediante SQLAlchemy.

## 3. Módulos funcionales

### 3.1 Inicio de sesión y permisos

El acceso se realiza mediante `POST /auth/login`. El backend verifica el usuario, la contraseña y que la cuenta esté activa. Si los datos son correctos, entrega un token JWT con la información del usuario y su rol.

La navegación de Angular protege las vistas:

- **ADMINISTRADOR:** puede acceder a Inicio y a los módulos de gestión.
- **OPERADOR:** tiene acceso al Control de acceso.

El token se utiliza para mantener la sesión de usuario en el frontend.

### 3.2 Propietarios

El módulo de Clientes registra y administra los propietarios. Cada propietario tiene identificación, nombre completo y teléfono. La identificación es única.

Un propietario puede tener varios vehículos y también puede tener suscripciones. La relación se conserva mediante el identificador interno `cliente_id`.

### 3.3 Vehículos y asociación con propietario

El módulo de Vehículos permite registrar, consultar, actualizar y eliminar vehículos. Cada vehículo guarda su placa, marca, color, modelo, tipo y, cuando está asociado, el `cliente_id` de su propietario.

La asociación se puede realizar al registrar el vehículo o posteriormente desde la gestión correspondiente. Un vehículo sin propietario asociado no puede utilizar una suscripción del sistema, porque las suscripciones pertenecen al propietario y no directamente a la placa.

### 3.4 Celdas

El módulo de Celdas administra los espacios del parqueadero. Cada celda tiene un código y un tipo. El backend mantiene su información y permite consultar las celdas y su disponibilidad.

En los procesos de contratación se ofrecen las celdas disponibles. Una celda ocupada por una estancia abierta o reservada por una suscripción activa no debe asignarse a otra contratación.

### 3.5 Operadores

El módulo de Operadores administra los trabajadores que registran las entradas y salidas. Cada movimiento de un vehículo conserva el operador que realizó la operación.

### 3.6 Control de acceso: entrada

El flujo de entrada de un vehículo es el siguiente:

1. El operador escribe la placa.
2. El frontend consulta `GET /estancias/vehiculo/{placa}`.
3. El backend localiza el vehículo y obtiene su propietario mediante `vehiculo.cliente_id`.
4. Busca una suscripción del propietario que esté en estado `ACTIVA`, dentro de su periodo de vigencia y que tenga al menos un pago registrado.
5. Si existe una suscripción válida, la respuesta incluye sus datos, entre ellos `celda_id`.
6. El formulario debe seleccionar la celda asociada a esa suscripción. Como las celdas reservadas no aparecen en el listado general de disponibles, el frontend consulta la celda específica por su ID y la incorpora únicamente a las opciones de esa entrada.
7. Al confirmar, el frontend envía placa, celda y operador a `POST /estancias/entrada`.
8. El backend vuelve a comprobar la suscripción, su vigencia, el pago, que la celda corresponda a esa suscripción, la compatibilidad entre vehículo y celda, y que ni el vehículo ni la celda estén ocupados.
9. Si las validaciones pasan, se crea la estancia abierta.

La selección automática de la celda en el formulario es una ayuda de interfaz; la validación definitiva siempre se realiza en el backend.

Si el vehículo no tiene propietario asociado o el propietario no tiene una suscripción pagada y vigente, el backend rechaza el ingreso por el flujo de suscripción. El Control de acceso contempla el registro de un vehículo nuevo y la asociación o creación de su propietario, además del flujo para contratar un plan cuando corresponde.

### 3.7 Control de acceso: salida

1. El operador consulta la placa.
2. El backend informa si el vehículo tiene una estancia abierta y en qué celda se encuentra.
3. El operador registra la salida.
4. El backend localiza la estancia abierta y guarda la fecha y hora de salida y el operador que la registró.

Una estancia se considera abierta cuando `salida` es `NULL`. Al cerrarla, la celda deja de estar ocupada por esa estancia.

## 4. Gestión de pagos y suscripciones

El módulo de Gestión de pagos agrupa cuatro procesos: planes, contrataciones, suscripciones e historial de pagos.

### 4.1 Planes

Un plan contiene nombre, descripción opcional, precio, duración en días y estado activo/inactivo. Solo los planes activos se ofrecen para nuevas contrataciones y renovaciones. Desactivar un plan evita nuevas operaciones con él, pero no elimina el historial de suscripciones existentes.

### 4.2 Contratación de un plan

1. Se busca al propietario mediante su identificación.
2. El sistema carga los planes activos y las celdas disponibles.
3. Se seleccionan plan, celda y método de pago. La referencia de pago es opcional.
4. El frontend envía los datos a `POST /pagos/contratar`.
5. El backend comprueba que el propietario exista, que el plan esté activo, que el valor recibido coincida con el precio del plan y que la celda exista, no esté eliminada, no esté reservada y no esté ocupada.
6. El backend crea la suscripción con propietario, plan, celda, fecha de inicio, fecha de finalización y estado `ACTIVA`.
7. En la misma transacción crea el pago asociado a esa suscripción.

La contratación y el pago se guardan como una sola operación transaccional: si falla una parte, no debe quedar una contratación incompleta.

### 4.3 Suscripciones

Las suscripciones relacionan tres registros: propietario (`cliente_id`), plan (`plan_id`) y celda (`celda_id`). También conservan fechas de vigencia y estado.

Los estados contemplados son:

- `ACTIVA`: suscripción vigente o pendiente de vencer.
- `VENCIDA`: terminó su periodo de vigencia.
- `CANCELADA`: fue cancelada.

Al consultar las suscripciones de un propietario, el sistema primero busca al propietario por identificación y después consulta sus suscripciones usando su ID interno.

### 4.4 Renovación

La renovación se realiza sobre una suscripción existente. El backend verifica que exista y que no esté cancelada, valida el nuevo plan y el valor del pago, conserva la celda asociada y calcula el siguiente periodo. Si la suscripción aún no ha terminado, el nuevo periodo comienza después de su fecha de finalización; si ya terminó, comienza desde el momento de la renovación.

Al actualizar las fechas y el plan, registra un nuevo pago asociado a la misma suscripción. Ambas operaciones se ejecutan dentro de una transacción.

### 4.5 Cancelación

La cancelación cambia el estado de la suscripción a `CANCELADA`. Una suscripción cancelada no puede renovarse mediante el flujo normal de renovación. El registro se conserva para mantener la trazabilidad.

### 4.6 Historial de pagos

Cada pago pertenece a una suscripción y registra valor, fecha, método de pago y referencia opcional. El historial general consulta los pagos registrados; también existe una consulta de pagos por suscripción.

El sistema utiliza la existencia de un pago asociado como parte de la validación de una suscripción pagada para el Control de acceso.

## 5. Relaciones principales de datos

```text
CLIENTE (propietario)
  ├── VEHICULO (uno o varios)
  └── SUSCRIPCION (una o varias)
        ├── PLAN
        ├── CELDA
        └── PAGO (uno o varios)

VEHICULO
  └── ESTANCIA (historial de entradas y salidas)
        ├── CELDA
        ├── OPERADOR DE ENTRADA
        └── OPERADOR DE SALIDA
```

La suscripción pertenece al propietario, no a una placa específica. Por eso el Control de acceso recorre la relación placa → vehículo → propietario → suscripción → celda.

## 6. Rutas principales de la API

| Método | Ruta | Función |
|---|---|---|
| `POST` | `/auth/login` | Iniciar sesión |
| `GET` | `/health` | Comprobar que la API responde |
| `GET/POST` | `/clientes` | Listar y crear propietarios |
| `GET` | `/clientes/identificacion/{identificacion}` | Buscar propietario por identificación |
| `GET/PATCH/DELETE` | `/clientes/{id}` | Consultar, actualizar o eliminar propietario |
| `GET/POST` | `/vehiculos` | Listar y registrar vehículos |
| `GET/PATCH/DELETE` | `/vehiculos/{id}` | Consultar, actualizar o eliminar vehículo |
| `GET/POST` | `/celdas` | Listar y crear celdas |
| `GET` | `/celdas/disponibles` | Consultar celdas disponibles |
| `GET` | `/celdas/{id}` | Consultar una celda específica |
| `GET/POST` | `/operadores` | Listar y crear operadores |
| `POST` | `/estancias/entrada` | Registrar entrada |
| `POST` | `/estancias/salida` | Registrar salida |
| `GET` | `/estancias/vehiculo/{placa}` | Consultar estado del vehículo y su suscripción |
| `GET/POST` | `/planes` | Listar y crear planes |
| `PATCH` | `/planes/{plan_id}` | Actualizar un plan |
| `PATCH` | `/planes/{plan_id}/desactivar` | Desactivar un plan |
| `POST` | `/pagos/contratar` | Contratar plan y registrar pago |
| `GET` | `/pagos` | Consultar historial de pagos |
| `GET` | `/pagos/suscripcion/{suscripcion_id}` | Consultar pagos de una suscripción |
| `GET` | `/suscripciones/cliente/{cliente_id}` | Consultar suscripciones del propietario |
| `GET` | `/suscripciones/{suscripcion_id}` | Consultar una suscripción |
| `POST` | `/suscripciones/{suscripcion_id}/renovar` | Renovar y registrar pago |
| `POST` | `/suscripciones/{suscripcion_id}/cancelar` | Cancelar suscripción |

La documentación interactiva de las rutas está disponible en `/docs` cuando el backend está ejecutándose.

## 7. Configuración e instalación local

### Requisitos

- Python 3.13 recomendado por la configuración documentada del backend.
- Node.js y npm compatibles con Angular 22.
- PostgreSQL.

### 7.1 Configurar backend

En PowerShell:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
```

Edita `backend/.env` con los datos de tu PostgreSQL y agrega una clave secreta privada para JWT:

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=autos_colombia
DB_USER=postgres
DB_PASSWORD=TU_CLAVE_LOCAL
DB_CONNECT_TIMEOUT=5
JWT_SECRET_KEY=UNA_CLAVE_SECRETA_LARGA_Y_PRIVADA
```

No publiques `.env`, contraseñas ni claves JWT en GitHub. `.env.example` debe contener únicamente valores de ejemplo.

Comprueba la conexión y ejecuta las migraciones cuando corresponda:

```powershell
.\.venv\Scripts\python.exe .\check_db.py
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini current
.\.venv\Scripts\python.exe -m alembic -c .\alembic.ini upgrade head
```

Inicia la API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000`
Documentación API: `http://127.0.0.1:8000/docs`

### 7.2 Configurar frontend

En otra terminal de PowerShell:

```powershell
cd frontend
npm.cmd ci
npm.cmd start -- --host 127.0.0.1 --port 4200
```

Frontend: `http://127.0.0.1:4200`

El frontend utiliza el proxy de desarrollo para enviar las solicitudes de API al backend local. Si se modifica la configuración del proxy, reinicia el servidor Angular. Para producción debe configurarse el destino de la API en el servidor web; el proxy de desarrollo no forma parte del build.

## 8. Pruebas y validaciones

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
cd frontend
npm.cmd run build
npm.cmd test -- --watch=false
```

Las pruebas automatizadas verifican comportamientos con datos simulados, según cada conjunto de pruebas. La compilación del frontend comprueba que Angular y TypeScript puedan construir la aplicación; no sustituye las pruebas funcionales contra una base de datos real.

## 9. Reglas importantes del negocio

- La identificación del propietario debe ser única.
- La placa identifica al vehículo y se relaciona con su propietario mediante `cliente_id`.
- Una suscripción se vincula al propietario, a un plan y a una celda.
- Una suscripción válida para ingresar debe estar activa, dentro de sus fechas y tener al menos un pago asociado.
- El ingreso debe utilizar la celda asignada a la suscripción.
- Una celda no puede tener simultáneamente dos estancias abiertas ni dos suscripciones activas.
- Un vehículo no puede tener dos estancias abiertas al mismo tiempo.
- La compatibilidad de celda se valida en el backend según el tipo de vehículo.
- Las operaciones críticas de contratación, renovación, entrada y salida se procesan con transacciones y validaciones en el servidor.

---

**Proyecto:** AutosColombia  
**Descripción:** Sistema de administración de parqueadero con control de acceso y gestión de planes, suscripciones y pagos.
