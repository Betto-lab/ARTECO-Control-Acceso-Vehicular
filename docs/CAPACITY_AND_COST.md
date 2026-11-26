# Capacidad, SLA y costo estimado

## Supuestos ejecutivos

ARTECO se dimensiona inicialmente para un condominio o sede empresarial con
operación continua. Al no existir todavía telemetría histórica, estas cifras
son supuestos académicos que deben revisarse después de medir el uso real.

| Indicador | Objetivo inicial |
| --- | ---: |
| Usuarios concurrentes habituales | 10 |
| Usuarios concurrentes en hora pico | 30 |
| Umbral de diseño | 50 |
| Margen sobre el pico esperado | 20 % |
| Solicitudes sostenidas al API | 10 por segundo |
| Ráfaga permitida | 20 solicitudes |
| Disponibilidad mensual objetivo | 99,5 % |
| Latencia de autorización objetivo | Menor de 3 s en el percentil 95 |
| Retención de logs | 365 días |
| Retención de copias de Aurora | 7 días |
| Horario operativo DEV propuesto | Lunes a viernes, 07:00-19:00 (America/Lima) |

El umbral de 50 usuarios cubre el pico estimado de 30 y deja capacidad para
crecimiento o eventos extraordinarios. API Gateway aplica actualmente un
límite de 10 solicitudes por segundo y una ráfaga de 20 para proteger la
base de datos y controlar costos.

## Estrategia por ambiente

| Ambiente | Propósito | Despliegue |
| --- | --- | --- |
| DEV | Desarrollo, pruebas funcionales y demostración | Activo, con componentes costosos reducidos |
| QA | Pruebas integrales previas a producción | Definido mediante `qa.tfvars`; despliegue manual y temporal |
| PROD | Operación final con red privada y controles completos | Definido mediante `prod.tfvars`; requiere aprobación |

Cada ambiente tiene una clave de state separada en
`environments/{dev,qa,prod}.backend.hcl`. En DEV se usa la misma clave
`arteco/dev/terraform.tfstate` ya desplegada. QA y PROD no se han desplegado;
sus roles OIDC, permisos y presupuestos deben configurarse antes de ejecutar
un plan conectado a AWS. Nunca se deben combinar sus `tfvars` con el backend
de DEV.

DEV evita NAT Gateway y el endpoint privado de SQS porque las funciones que
usan Data API no necesitan permanecer dentro de la VPC. QA y PROD conservan
la topología privada completa para validar el diseño de producción.

El horario automático de Aurora está codificado mediante EventBridge Scheduler,
pero `enable_database_schedule=false` evita activarlo accidentalmente. Cuando el
grupo apruebe su uso, DEV puede iniciar a las 07:00 y detenerse a las 19:00 de
lunes a viernes. QA se crea solo durante pruebas y PROD permanece disponible
24x7 para cumplir el SLA.

## Ciclo de vida de almacenamiento

- Los objetos mayores de 128 KiB bajo `uploads/` pasan a `STANDARD_IA` a los
  30 días y a Glacier a los 90 días en DEV y QA; expiran a los 365 días.
- PROD conserva los objetos durante 730 días y retrasa las transiciones a 60
  y 180 días.
- Las versiones antiguas del frontend expiran después de 30 días en DEV, 90
  días en QA y 365 días en PROD.
- Las cargas multiparte incompletas se eliminan después de 7 días.

El umbral de 128 KiB evita pagar transiciones de objetos pequeños que no se
beneficiarían del almacenamiento infrecuente.

## Estimación preliminar

La estimación se basa en precios públicos de AWS y debe confirmarse en AWS
Pricing Calculator antes de aprobar PROD.

- Aurora Serverless v2 es el principal costo fijo. Con una capacidad mínima
  de 0,5 ACU durante todo el mes y una referencia de USD 0,12 por ACU-hora,
  el cómputo base es aproximadamente **USD 43,80 al mes**, sin incluir
  almacenamiento, I/O ni Data API.
- Lambda, API Gateway, S3 y CloudFront dependen principalmente del número de
  solicitudes y transferencia. Para el volumen académico inicial su costo es
  pequeño y puede permanecer dentro de los niveles gratuitos aplicables.
- CloudFront ofrece un nivel gratuito mensual amplio; S3 cobra por
  almacenamiento y solicitudes sin un compromiso mínimo.
- QA debe crearse solo durante las pruebas y destruirse al terminar para no
  duplicar el costo continuo de Aurora, NAT y endpoints privados.
- El presupuesto de USD 5 configurado en la cuenta es una **alerta temprana de
  DEV**, no una estimación del costo mensual de producción. Terraform conserva
  las alertas existentes de costo real al 85 % y 100 %, y previsión al 100 %.

## Presupuesto como código

`terraform/budget.tf` declara el presupuesto mensual
`ARTECO-Dev-Mensual-5USD`, con límite de USD 5 y notificaciones de gasto real
al 85 % (USD 4,25) y 100 %, además de previsión al 100 %. El recurso solo se
habilita en DEV.

El presupuesto se creó inicialmente desde la consola y se importó al state
remoto el 26 de noviembre de 2026. Esta es la orden utilizada; no debe
repetirse mientras el recurso permanezca en el state:

```bash
terraform -chdir=terraform import \
  -var-file=../environments/dev.tfvars \
  'aws_budgets_budget.dev_monthly[0]' \
  '755909808380:ARTECO-Dev-Mensual-5USD'
```

Después de la importación, `terraform plan` mostró cero cambios para el
presupuesto. La evidencia está en `docs/EVIDENCE.md`.

## Atributos de calidad

- **Disponibilidad:** CloudFront, API Gateway y Aurora administrados reducen
  puntos únicos de falla; PROD debe considerar réplica de base de datos si el
  SLA aumenta.
- **Rendimiento:** CDN para archivos estáticos, API con límites explícitos y
  Aurora Serverless con escalamiento de 0,5 a 2 ACU.
- **Seguridad:** frontend privado en S3, acceso únicamente mediante CloudFront,
  cifrado en reposo y OIDC sin llaves permanentes en GitHub.
- **Escalabilidad:** servicios serverless y umbral de 50 usuarios concurrentes.
- **Mantenibilidad:** Terraform aprovisiona infraestructura y Ansible publica
  la aplicación de forma repetible.
- **Costo:** presupuesto, límites del API y ambientes no productivos temporales.

## Fuentes de precios

- <https://aws.amazon.com/rds/aurora/pricing/>
- <https://aws.amazon.com/cloudfront/pricing/>
- <https://aws.amazon.com/s3/pricing/>
