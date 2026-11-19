# ARTECO - Control de Acceso Vehicular

Repositorio académico para evolucionar una base serverless de AWS hacia el proyecto ARTECO. El objetivo es recibir y procesar eventos de ingreso y salida vehicular con infraestructura definida en Terraform.

> **Estado: backend DEV funcional y persistente.** API Gateway, Lambda y Aurora
> autorizan vehículos y conservan los eventos reales. El frontend está definido
> para publicarse de forma privada con S3, CloudFront, Terraform y Ansible.

## Alcance disponible

- Infraestructura base: API Gateway, Lambda, Aurora, S3, CloudFront, SQS/DLQ, VPC, IAM y CloudWatch.
- Registro, autorización y persistencia de eventos en `lambda/vehicle_access/index.py`.
- Publicación repetible del frontend mediante `ansible/deploy_frontend.yml`.
- Documentación de arquitectura, límites y pendientes en `docs/ARTECO.md`.
- Correcciones de Checkov para retención de logs y cifrado de SQS.

## Flujo objetivo

```text
Usuario -> CloudFront -> S3 (frontend)
                         |
                         +-> API Gateway -> Lambda de acceso -> Aurora
```

El flujo existente de carga y procesamiento de archivos se conserva como base técnica reutilizable, pero todavía no está adaptado por completo al dominio vehicular.

## Despliegue DEV validado

- API base: `https://mws54355qd.execute-api.us-east-2.amazonaws.com`
- `POST /upload`: probado con respuesta HTTP `200`; almacena el archivo en S3 y publica el trabajo en SQS.
- `POST /vehicle-access`: protegido por Cognito; una solicitud sin token devuelve HTTP `401`.
- `POST /demo/vehicle-access`: registra vehículos, autoriza accesos y persiste eventos en Aurora.
- Apply manual #12 ejecutado correctamente mediante GitHub OIDC.
- NAT Gateway y el endpoint de interfaz SQS permanecen desactivados en DEV para limitar costos.

La lectura automática de placas y el reconocimiento facial permanecen como
integraciones posteriores. Consulta [docs/EVIDENCE.md](docs/EVIDENCE.md) para
los resultados y enlaces verificables.

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
ansible/            Publicación y configuración del frontend
lambda/             Validación, IA, registro y alertas
database/           Esquema PostgreSQL versionado
frontend/           Panel web estático de demostración
tests/              Pruebas unitarias sin dependencias AWS
environments/       Variables DEV, QA y PROD
docs/               Arquitectura, Checkov y evidencias
.github/workflows/  Pruebas, Terraform y Checkov en cada PR
```

## Servicios avanzados

Aurora Serverless v2 está activo en DEV para la demostración persistente.
Cognito protege la ruta vehicular, Rekognition analiza evidencias privadas en
S3, SNS publica alertas y SQS desacopla el registro. Los supuestos de SLA,
capacidad y costo están en [docs/CAPACITY_AND_COST.md](docs/CAPACITY_AND_COST.md).

Más información: [arquitectura](docs/ARCHITECTURE.md), [Checkov](docs/CHECKOV.md) y [evidencias](docs/EVIDENCE.md).
