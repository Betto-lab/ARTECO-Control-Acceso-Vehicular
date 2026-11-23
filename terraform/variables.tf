variable "project_name" {
  description = "Nombre base del proyecto"
  type        = string
  default     = "arteco"
}

variable "environment" {
  description = "Entorno de despliegue: dev, qa o prod"
  type        = string

  validation {
    condition     = contains(["dev", "qa", "prod"], var.environment)
    error_message = "El environment debe ser dev, qa o prod."
  }
}

variable "aws_region" {
  description = "Region de AWS"
  type        = string
  default     = "us-east-2"
}

variable "aws_profile" {
  description = "Perfil de AWS CLI usado por Terraform"
  type        = string
  default     = "betto-admin"
}

variable "vpc_cidr" {
  description = "CIDR principal de la VPC"
  type        = string
}

variable "enable_database" {
  description = "Crea Aurora Serverless v2. Mantener false en validaciones locales para evitar costos."
  type        = bool
  default     = false
}

variable "enable_database_schedule" {
  description = "Programa encendido y apagado de Aurora no productivo. Requiere enable_database=true y permanece desactivado por defecto."
  type        = bool
  default     = false
}

variable "database_schedule_timezone" {
  description = "Zona horaria IANA usada por los horarios de Aurora."
  type        = string
  default     = "America/Lima"
}

variable "database_start_schedule" {
  description = "Expresion EventBridge Scheduler para iniciar Aurora DEV."
  type        = string
  default     = "cron(0 7 ? * MON-FRI *)"
}

variable "database_stop_schedule" {
  description = "Expresion EventBridge Scheduler para detener Aurora DEV."
  type        = string
  default     = "cron(0 19 ? * MON-FRI *)"
}

variable "enable_sqs_vpc_endpoint" {
  description = "Crea el endpoint privado de SQS. Desactivarlo cuando Lambda no usa VPC evita su costo por hora."
  type        = bool
  default     = true
}

variable "enable_lambda_vpc" {
  description = "Conecta las funciones Lambda a las subredes privadas. Desactivarlo en dev permite usar servicios AWS sin NAT."
  type        = bool
  default     = true
}

variable "enable_nat_gateway" {
  description = "Crea NAT Gateways para la salida de las subredes privadas. Desactivarlo evita su costo por hora."
  type        = bool
  default     = true
}

variable "database_name" {
  description = "Nombre lógico de la base de datos ARTECO"
  type        = string
  default     = "arteco"
}

variable "alert_email" {
  description = "Correo opcional para suscripción SNS; vacío evita crear la suscripción."
  type        = string
  default     = ""
}
