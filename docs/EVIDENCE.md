# Evidencias por integrante

## Estado de DEV — 26 de noviembre de 2026

- Presupuesto mensual de USD 5 importado al state remoto: https://github.com/Betto-lab/ARTECO-Control-Acceso-Vehicular/actions/runs/45756755986
- Plan posterior a la alineación del presupuesto: https://github.com/Betto-lab/ARTECO-Control-Acceso-Vehicular/actions/runs/45817147460 — `9 to add, 0 to change, 0 to destroy`.
- Intento de publicar el frontend: https://github.com/Betto-lab/ARTECO-Control-Acceso-Vehicular/actions/runs/45817672799 — falló por permisos IAM faltantes para crear el bucket S3, crear el control de acceso de CloudFront y configurar el ciclo de vida S3. Ansible no llegó a ejecutarse. El frontend todavía no está desplegado.


## Despliegue DEV — 18 de noviembre de 2026

- Apply final exitoso: https://github.com/Betto-lab/ARTECO-Control-Acceso-Vehicular/actions/runs/44365811942
- Plan posterior al despliegue: https://github.com/Betto-lab/ARTECO-Control-Acceso-Vehicular/actions/runs/44365596939
- Resultado del plan posterior: `No changes. Your infrastructure matches the configuration.`
- API base: `https://mws54355qd.execute-api.us-east-2.amazonaws.com`
- Prueba `POST /upload`: HTTP `200`, archivo aceptado con clave `uploads/86476cab-8b5f-4032-8920-c989db173ac5.bin`.
- Prueba `POST /vehicle-access` sin token: HTTP `401 Unauthorized`, confirmando que el autorizador Cognito protege la ruta.

La prueba de carga confirma que la Lambda pudo escribir en S3 y enviar el mensaje a SQS antes de devolver HTTP `200`. La comprobación independiente del objeto procesado queda pendiente porque el entorno local no dispone de un perfil AWS administrativo. Tampoco se afirma todavía autorización vehicular ni persistencia de accesos.

Cada participante debe crear su propia rama y pull request. No se deben reutilizar capturas de otra cuenta.

## Marielsys — `marielsysm19-cpu`

- Identificación: captura del resultado inicial de Checkov para `CKV_AWS_338` y `CKV_AWS_27`.
- Antes del commit: captura de `git diff -- terraform/cloudwatch.tf terraform/sqs.tf`.
- Después del commit: captura del commit y del pull request pertenecientes a su cuenta.
- Verificación: captura de Checkov con 5 comprobaciones aprobadas y 0 fallidas.

## Pendiente para los demás integrantes

Cada integrante debe registrar dos hallazgos distintos, la corrección aplicada, su commit y el enlace de su PR.
