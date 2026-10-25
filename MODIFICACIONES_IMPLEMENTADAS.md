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



