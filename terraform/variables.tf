variable "project_name" {
  description = "Nombre base del proyecto"
  type        = string
  default     = "aws-lambda-integration"
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