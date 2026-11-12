# ARTECO - Control de Acceso Vehicular

Repositorio académico para evolucionar una base serverless de AWS hacia el proyecto ARTECO. El objetivo es recibir y procesar eventos de ingreso y salida vehicular con infraestructura definida en Terraform.

> **Estado: prototipo en desarrollo.** El repositorio no representa una implementación completa ni confirma que ARTECO esté desplegado en AWS. La función de acceso vehicular valida el contrato de entrada, pero la autorización, persistencia y lectura automática de placas siguen pendientes.

## Alcance disponible

- Infraestructura base: API Gateway, Lambda, S3, SQS/DLQ, VPC, IAM y CloudWatch.
- Prototipo verificable de validación de eventos en `lambda/vehicle_access/index.py`.
- Documentación de arquitectura, límites y pendientes en `docs/ARTECO.md`.
- Correcciones de Checkov para retención de logs y cifrado de SQS.

## Flujo objetivo

```text
Sensor/operador -> API Gateway -> Lambda de acceso -> autorización (pendiente)
                                      |
                                      +-> SQS -> procesamiento/auditoría (pendiente)
```

El flujo existente de carga y procesamiento de archivos se conserva como base técnica reutilizable, pero todavía no está adaptado por completo al dominio vehicular.

## Validación local sin desplegar

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
terraform -chdir=terraform fmt -check
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
docker run --rm -v "${PWD}:/repo" bridgecrew/checkov:latest -d /repo/terraform --check CKV_AWS_338,CKV_AWS_27
```

Los comandos anteriores validan código y configuración. No ejecutan `terraform plan` ni `terraform apply`, y no crean recursos ni gastos en AWS.

## Seguridad corregida

| Regla | Corrección |
|---|---|
| `CKV_AWS_338` | Los grupos de CloudWatch conservan logs por 365 días. |
| `CKV_AWS_27` | La cola principal y la DLQ usan cifrado administrado por SQS. |

Consulta [docs/ARTECO.md](docs/ARTECO.md) para el alcance real y los pendientes.
