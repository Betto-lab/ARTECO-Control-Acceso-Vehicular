# Permisos de despliegue Terraform para DEV

`ARTECO-Terraform-Deploy-Dev.json` es la política candidata para que el rol
`arteco-github-actions-dev` pueda crear y destruir la infraestructura definida
en `terraform/` para la cuenta `755909808380` y la región `us-east-2`.

La política de despliegue es independiente de las políticas existentes de
estado remoto y lectura. No concede acceso al rol antiguo
`arteco-github-actions-terraform`.

## Uso controlado

1. Revisar la política antes de adjuntarla.
2. Adjuntarla únicamente a `arteco-github-actions-dev`.
3. Ejecutar el workflow manual desde la rama `development`.
4. Para adoptar el presupuesto creado en consola, seleccionar
   `import-budget` y escribir `IMPORT`. Esta operación no crea infraestructura.
5. Ejecutar `destroy` al terminar la demostración.
6. Confirmar que el state no contiene recursos y retirar la política de
   despliegue si ya no se necesita.

La primera ejecución puede revelar alguna acción de lectura adicional exigida
por el proveedor AWS. Si ocurre, se debe agregar solo la acción indicada por el
error, volver a validar y documentar el cambio.
