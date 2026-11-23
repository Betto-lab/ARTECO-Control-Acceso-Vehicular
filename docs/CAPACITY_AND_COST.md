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

DEV evita NAT Gateway y el endpoint privado de SQS porque las funciones que
usan Data API no necesitan permanecer dentro de la VPC. QA y PROD conservan
la topología privada completa para validar el diseño de producción.

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
  DEV**, no una estimación del costo mensual de producción.

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
