# Modificaciones realizadas en AutosColombia

## 1. Introducción

En este documento se describen las modificaciones que se van realizando al sistema AutosColombia a partir del código proporcionado inicialmente por el profesor.

El objetivo es mejorar el funcionamiento del sistema, facilitar su uso y adaptar sus funcionalidades a las necesidades del proyecto.

## 2. Modificaciones realizadas

### 2.1. Organización de las celdas

Se registraron 80 celdas para el estacionamiento, distribuidas en 70 espacios para automóviles y 10 para motocicletas.

### 2.2. Disponibilidad de las celdas

Se modificó el sistema para que, al registrar la entrada de un vehículo, se muestren únicamente las celdas disponibles. Si una celda está ocupada, deja de aparecer entre las opciones para una nueva entrada.

## 3. Control de ocupación de celdas

Se implementó una mejora en el módulo de administración de celdas para facilitar el seguimiento de los espacios disponibles y ocupados dentro de Autos Colombia.

**Cambios realizados:**

- **Estado de las celdas:** se incorporó una columna llamada «Estado» en la tabla de administración, que permite identificar si una celda está disponible u ocupada.
- **Identificación visual:** las celdas disponibles se muestran con una etiqueta verde y las ocupadas con una etiqueta roja.
- **Resumen de ocupación:** se añadieron indicadores que muestran la cantidad total de celdas disponibles y ocupadas.
- **Cálculo automático:** el estado se determina a partir de los registros de estancia en la base de datos. Una celda se considera ocupada cuando tiene una estancia sin fecha de salida registrada.
- **Integración con el backend:** se actualizaron el servicio de celdas y los esquemas de respuesta para incluir el estado de cada celda y los totales de ocupación.
- **Actualización del frontend:** se adaptaron los modelos de TypeScript, el componente de administración, la tabla y los estilos visuales para presentar la información.
- **Diseño adaptable:** los indicadores se ajustan a pantallas pequeñas para facilitar su consulta desde dispositivos móviles.

**Resultado:** el administrador puede consultar la disponibilidad general de los espacios y reconocer el estado individual de cada celda sin modificar manualmente su estado ni alterar el funcionamiento del formulario de registro de entradas.

**Consideración técnica:** el estado se calcula a partir de las estancias registradas; no se almacena como un campo independiente en la tabla de celdas.

## 4. Registro automático de vehículos nuevos desde Control de acceso

### Descripción de la mejora

Se implementó un flujo que permite registrar un vehículo nuevo y confirmar su entrada al parqueadero desde la pantalla **Control de acceso**, sin tener que registrarlo previamente desde el módulo de gestión de vehículos.

### Justificación de la mejora

Esta lógica surgió de la necesidad de facilitar el trabajo del operario y evitar que tuviera que abandonar la pantalla de Control de acceso para registrar previamente cada vehículo nuevo. Al consultar una placa, el sistema puede determinar si el vehículo ya está registrado o si debe solicitar sus datos antes de permitir el ingreso.

De esta manera, el operario puede identificar qué vehículos ya están registrados en el sistema y cuáles todavía no, completar el registro de los nuevos directamente desde el control de acceso y confirmar su entrada en un mismo flujo. Esto agiliza la atención, reduce los pasos manuales y ayuda a mantener actualizada la información de los vehículos y la ocupación de las celdas.

### Funcionamiento

1. El usuario introduce la placa del vehículo.
2. El sistema consulta si el vehículo ya está registrado.
3. Si la placa no existe, se abre un modal para ingresar la marca, el modelo, el color y el tipo de vehículo.
4. El usuario selecciona una celda compatible y el operador responsable de la entrada.
5. El sistema registra el vehículo y su entrada mediante una única operación.
6. Tras completar el registro, el vehículo aparece en la gestión de vehículos y la celda queda ocupada.

### Compatibilidad entre vehículos y celdas

- **MOTO:** utiliza celdas de tipo `Moto`.
- **AUTOMOVIL:** utiliza celdas de tipo `Automovil`.
- **CAMIONETA:** utiliza las mismas celdas que los automóviles.

La selección de celdas compatibles se actualiza según el tipo de vehículo seleccionado.
