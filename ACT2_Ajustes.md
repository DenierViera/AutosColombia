
## 1. Inicio de sesión

El sistema cuenta con un módulo de autenticación que permite ingresar mediante un nombre de usuario y una contraseña.

Para acceder, el usuario debe tener credenciales previamente registradas en el sistema.

### Tipos de usuario

## CREDENCIALES

Credenciales Admin
Username: Admin 17
Password: controler_17_xt

Credenciales Operador
Username: DenierAndres
Password: Trabajador1#

Actualmente existen dos roles:

**Administrador**
- Accede al panel administrativo.
- Puede consultar la página de inicio.
- Puede gestionar operadores, celdas y vehículos.
- Puede acceder al módulo de Control de acceso.

**Operador**
- Accede únicamente al módulo de Control de acceso.
- Puede realizar las operaciones de registro de entradas y salidas de vehículos.
- No visualiza las opciones del panel administrativo.

### Funcionamiento del login

1. El usuario ingresa su nombre de usuario y contraseña.
2. El sistema envía las credenciales al backend para su validación.
3. Si los datos son correctos, el servidor devuelve un token de autenticación y la información del usuario.
4. El sistema almacena el token y los datos de la sesión.
5. Según el rol asignado, el usuario es dirigido a su interfaz correspondiente.

### Redirección según el rol

| Rol | Ruta de acceso |
|---|---|
| ADMINISTRADOR | `/` (Inicio) |
| OPERADOR | `/control-acceso` |

### Seguridad

- Las contraseñas se almacenan mediante hash, no como texto plano.
- El acceso a las rutas se controla mediante guards de Angular.
- El token permite identificar la sesión autenticada.

## 2. Incorporación de credenciales para operadores

Se modificó el módulo de Gestión de operadores para permitir que cada operador tenga credenciales propias de acceso al sistema.

Anteriormente, el registro de operadores únicamente almacenaba su información personal. Con esta modificación, también se permite crear y administrar sus credenciales de autenticación.

### Funcionalidades implementadas

- Crear un nombre de usuario y una contraseña al registrar un operador.
- Asociar las credenciales con el operador correspondiente.
- Visualizar el nombre de usuario en el listado de operadores.
- Mostrar la contraseña de forma enmascarada en la interfaz.
- Editar el nombre de usuario y restablecer la contraseña.
- Activar o desactivar las credenciales de acceso de cada operador.

### Funcionamiento

1. El administrador registra un operador e ingresa sus datos personales.
2. Asigna un nombre de usuario y una contraseña.
3. El sistema almacena la contraseña mediante un algoritmo de hash.
4. Las credenciales quedan asociadas al operador registrado.
5. El operador puede utilizar sus credenciales para iniciar sesión.
6. El administrador puede habilitar o deshabilitar su acceso cuando sea necesario.

### Seguridad de las credenciales

Las contraseñas no se almacenan en texto plano, sino mediante hash.

Por esta razón, el administrador no puede consultar la contraseña original. Si el operador la olvida, el administrador puede establecer una nueva mediante la edición de sus credenciales.

### Control del acceso

El administrador dispone de un estado de acceso para cada operador:

- **Activo:** permite al operador iniciar sesión.
- **Desactivado:** impide que el operador inicie sesión.

Esta modificación permite gestionar de manera centralizada los usuarios autorizados para realizar operaciones dentro del parqueadero.