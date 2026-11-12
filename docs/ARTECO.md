# ARTECO: control de acceso vehicular

## Estado actual

Este repositorio contiene una base serverless reutilizable y un **prototipo no desplegado** para validar eventos de ingreso y salida vehicular. No se afirma que exista todavía un sistema completo de reconocimiento de placas, autorización o persistencia de accesos.

El prototipo se encuentra en `lambda/vehicle_access/index.py` y acepta:

```json
{
  "plate": "ABC-123",
  "event_type": "ENTRY",
  "gate_id": "gate-01"
}
```

La respuesta usa el estado `accepted_for_prototype` y declara explícitamente `authorization_checked: false` y `persistence_completed: false`.

## Componentes reutilizados

- API Gateway y Lambda como base de entrada serverless.
- SQS y DLQ para procesamiento asíncrono.
- S3 para evidencias o archivos asociados.
- CloudWatch para registros y alertas.
- Terraform para describir la infraestructura sin ejecutarla en esta actividad.

## Pendientes antes de una implementación real

- Conectar la función `vehicle_access` a una ruta propia de API Gateway.
- Definir el origen confiable de vehículos autorizados y su modelo de datos.
- Persistir eventos con idempotencia y trazabilidad.
- Integrar un proveedor de lectura de placas y evaluar precisión/privacidad.
- Añadir autenticación, autorización, pruebas de integración y manejo de datos personales.
- Revisar costos, retención de datos y controles operativos antes de cualquier despliegue.

## Correcciones de seguridad incluidas en la rama

| Checkov | Archivo | Cambio |
|---|---|---|
| `CKV_AWS_338` | `terraform/cloudwatch.tf` | Retención explícita de 365 días para los tres grupos de logs. |
| `CKV_AWS_27` | `terraform/sqs.tf` | Cifrado administrado por SQS habilitado en la cola principal y la DLQ. |

Estas correcciones se verifican estáticamente. No requieren ni autorizan ejecutar `terraform apply`.
