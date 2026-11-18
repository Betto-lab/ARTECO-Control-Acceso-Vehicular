# ARTECO - Control de Acceso Vehicular

Repositorio académico para evolucionar una base serverless de AWS hacia el proyecto ARTECO. El objetivo es recibir y procesar eventos de ingreso y salida vehicular con infraestructura definida en Terraform.

> **Estado: infraestructura DEV desplegada y prototipo funcional parcial.** La base serverless está desplegada en AWS y validada con Terraform, pero la autorización vehicular, la persistencia de accesos y la lectura automática de placas siguen pendientes.

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

## Despliegue DEV validado

- API base: `https://mws54355qd.execute-api.us-east-2.amazonaws.com`
- `POST /upload`: probado con respuesta HTTP `200`; almacena el archivo en S3 y publica el trabajo en SQS.
- `POST /vehicle-access`: protegido por Cognito; una solicitud sin token devuelve HTTP `401`.
- Terraform posterior al despliegue: `No changes`, confirmando que el estado remoto coincide con la configuración.
- Aurora, NAT Gateway y el endpoint de interfaz SQS permanecen desactivados en DEV para limitar costos.

La infraestructura desplegada no implica todavía un control vehicular completo end-to-end. Consulta [docs/EVIDENCE.md](docs/EVIDENCE.md) para los resultados y enlaces verificables.

## Validación local

Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
terraform -chdir=terraform fmt -check
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
docker run --rm -v "${PWD}:/repo" bridgecrew/checkov:latest -d /repo/terraform --check CKV_AWS_338,CKV_AWS_27
```

Los comandos anteriores validan código y configuración local. No modifican los recursos desplegados en AWS.

## Seguridad corregida

| Regla | Corrección |
|---|---|
| `CKV_AWS_338` | Los grupos de CloudWatch conservan logs por 365 días. |
| `CKV_AWS_27` | La cola principal y la DLQ usan cifrado administrado por SQS. |

Consulta [docs/ARTECO.md](docs/ARTECO.md) para el alcance real y los pendientes.

## Estructura completa

```text
terraform/          Infraestructura AWS y controles de seguridad
lambda/             Validación, IA, registro y alertas
database/           Esquema PostgreSQL versionado
frontend/           Panel web estático de demostración
tests/              Pruebas unitarias sin dependencias AWS
environments/       Variables DEV, QA y PROD
docs/               Arquitectura, Checkov y evidencias
.github/workflows/  Pruebas, Terraform y Checkov en cada PR
```

## Servicios avanzados

Aurora Serverless v2 está definido pero desactivado por defecto mediante `enable_database=false`. Cognito protege la ruta vehicular, Rekognition analiza evidencias privadas en S3, SNS publica alertas y SQS desacopla el registro.

Más información: [arquitectura](docs/ARCHITECTURE.md), [Checkov](docs/CHECKOV.md) y [evidencias](docs/EVIDENCE.md).
