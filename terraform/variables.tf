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
