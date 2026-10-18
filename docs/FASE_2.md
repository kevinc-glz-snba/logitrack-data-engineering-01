# Fase 2 — Infraestructura en Azure

## 1. Objetivo

Preparar en Microsoft Azure los servicios necesarios para almacenar, procesar y supervisar los datos de LogiTrack. La infraestructura se administra con Terraform para que pueda revisarse y reproducirse mediante código.

## 2. Herramientas utilizadas

- **Terraform:** define los recursos de Azure mediante archivos `.tf`.
- **Azure CLI:** permite iniciar sesión y consultar los recursos desde la terminal.
- **Azure Data Lake Storage Gen2:** almacena los archivos de datos.
- **Azure Data Factory:** se utilizará para organizar los procesos de ingesta.
- **Azure Key Vault:** permite administrar secretos de forma segura.
- **Log Analytics y Azure Monitor:** ayudan a revisar registros y configurar alertas.

## 3. Infraestructura implementada

| Recurso | Uso en el proyecto |
|---|---|
| Resource Group | Agrupa los recursos de LogiTrack. |
| Storage Account con ADLS Gen2 | Almacena los datos del proyecto. |
| Contenedor `bronze` | Datos originales recibidos de la fuente. |
| Contenedor `silver` | Datos limpios y preparados. |
| Contenedor `gold` | Datos listos para análisis. |
| Azure Data Factory | Orquestación de los pipelines en las siguientes fases. |
| Key Vault | Administración de secretos. |
| Log Analytics Workspace | Centralización de registros. |
| Monitor Action Group | Base para configurar notificaciones. |

Los contenedores son privados. El almacenamiento tiene habilitado el espacio de nombres jerárquico de ADLS Gen2.

## 4. Organización de los archivos

Los archivos se encuentran en la carpeta `infra/`:

```text
infra/
├── backend.tf
├── providers.tf
├── variables.tf
├── main.tf
├── outputs.tf
├── dev.tfvars
└── backends/
    ├── dev.hcl
    └── prod.hcl
```

- `main.tf`: recursos de Azure.
- `providers.tf`: proveedor de Terraform para Azure.
- `variables.tf`: región y entorno.
- `outputs.tf`: nombres de los recursos creados.
- `backend.tf`: declaración del estado remoto.
- `dev.tfvars`: valores para desarrollo.
- `backends/*.hcl`: configuración del backend por entorno.

El código admite los valores `dev` y `prod`, pero **solo se verificó el despliegue de `dev`**.

## 5. Pasos para desplegar o verificar

**Requisitos previos:** tener una suscripción activa de Azure, Azure CLI, Terraform y permisos sobre los recursos y el backend remoto. El almacenamiento usado para el estado remoto debe existir previamente.

### Paso 1. Iniciar sesión y seleccionar la suscripción

```bash
az login
az account show -o table
```

Si se trabaja con varias suscripciones, seleccionar la correcta antes de continuar:

```bash
az account set --subscription "ID_O_NOMBRE_DE_LA_SUSCRIPCION"
```

### Paso 2. Entrar a la carpeta de infraestructura

Desde la raíz del repositorio:

```bash
cd infra
```

### Paso 3. Conectar el backend remoto de desarrollo

```bash
terraform init -reconfigure -backend-config="backends/dev.hcl"
```

Este comando configura el acceso al estado remoto. No crea recursos de Azure.

### Paso 4. Validar el código

```bash
terraform fmt -check
terraform validate
```

Si `terraform fmt -check` indica diferencias de formato, se pueden corregir con `terraform fmt` y volver a validar.

### Paso 5. Revisar el plan

```bash
terraform plan -var-file="dev.tfvars"
```

El plan muestra si Terraform necesita crear, cambiar o eliminar recursos. **Debe revisarse antes de aplicar cualquier cambio.**

### Paso 6. Aplicar cambios (solo cuando sea necesario)

```bash
terraform apply -var-file="dev.tfvars"
```

En este proyecto **no fue necesario volver a ejecutar `apply`**, porque la infraestructura del primer intento ya estaba desplegada y el plan no mostró cambios.

### Paso 7. Consultar los recursos administrados

```bash
terraform state list
terraform output
```

Estos comandos permiten revisar qué recursos conoce Terraform y sus nombres de salida.

## 6. Validaciones realizadas

Se comprobó lo siguiente:

1. Terraform reconoció los recursos existentes mediante `terraform state list`.
2. `terraform init` terminó correctamente con el proveedor AzureRM `v4.81.0`.
3. `terraform validate` se ejecutó correctamente en el repositorio de entrega.
4. `terraform plan -var-file="dev.tfvars"` devolvió:

```text
No changes. Your infrastructure matches the configuration.
```

Este resultado indica que, al momento de la verificación, Terraform no proponía cambios para el entorno de desarrollo.

## 7. Seguridad y costos

- No se deben subir contraseñas, tokens ni archivos `*.tfstate` al repositorio.
- El estado de Terraform se almacena en un backend remoto.
- Los contenedores del Data Lake tienen acceso privado.
- La cuenta de almacenamiento está configurada para utilizar autenticación de Azure y TLS 1.2 como mínimo.
- Se trabaja primero con `dev` para evitar despliegues innecesarios.
- Antes de ejecutar `terraform apply`, se revisan los cambios y su posible costo.

## 8. Pendientes para las siguientes fases

La infraestructura ya está preparada, pero todavía faltan los procesos de datos:

- Conectar PostgreSQL local con Azure Data Factory.
- Crear y ejecutar el pipeline de ingesta hacia Bronze.
- Implementar transformaciones hacia Silver y Gold.
- Configurar los secretos, permisos y alertas que necesiten esos procesos.

**Nota:** el Action Group existe, pero aún no tiene destinatarios de notificación configurados. La existencia de los servicios no significa que los pipelines o las alertas ya estén funcionando.

## 9. Conclusión

En esta fase se reutilizó y verificó una infraestructura creada con Terraform en Microsoft Azure. Se confirmó que el entorno de desarrollo coincide con el código y que cuenta con los servicios necesarios para continuar con la ingesta y transformación de datos de LogiTrack.