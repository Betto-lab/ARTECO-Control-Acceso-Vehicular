# Checkov

## Correcciones de Marielsys

| Regla | Error identificado | Resolución |
|---|---|---|
| `CKV_AWS_338` | Los grupos de CloudWatch retenían logs por solo 7 días. | Se configuraron 365 días en los tres grupos de logs. |
| `CKV_AWS_27` | La cola SQS principal y la DLQ no declaraban cifrado. | Se habilitó `sqs_managed_sse_enabled = true` en ambas colas. |

## Comandos de evidencia

```powershell
docker run --rm -v "${PWD}:/repo" bridgecrew/checkov:latest -d /repo/terraform --check CKV_AWS_338,CKV_AWS_27 --compact
```

Resultado verificado localmente: 5 aprobadas y 0 fallidas para esas dos reglas.
