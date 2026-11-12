# Arquitectura ARTECO

## Flujo principal

1. Cognito autentica al operador del panel.
2. API Gateway recibe `POST /vehicle-access`.
3. `vehicle_access` normaliza y valida el evento.
4. `access_registration` genera un identificador idempotente y lo envía a SQS.
5. `plate_recognition` y `face_verification` consumen evidencias privadas de S3 mediante Rekognition.
6. Aurora conserva vehículos y eventos cuando `enable_database=true`.
7. `alerts` publica incidentes en SNS.
8. CloudWatch centraliza logs y la alarma de la DLQ.

## Control de costos

Aurora está desactivado de forma predeterminada con `enable_database=false`. La validación y Checkov no requieren credenciales ni crean recursos. Solo una decisión explícita de despliegue debe habilitar servicios con costo.

## Límites actuales

- El frontend ejecuta validación local y aún no almacena tokens Cognito.
- Las Lambdas de IA necesitan imágenes reales y permisos AWS para pruebas de integración.
- El esquema SQL se entrega como migración; su ejecución no es automática.
- No se incluyeron datos biométricos ni datos personales de ejemplo.
