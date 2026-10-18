variable "location" {
  type        = string
  description = "Region de Azure donde se desplegaran los recursos de LogiTrack"
  default     = "eastus2"
}

variable "environment" {
  type        = string
  description = "Entorno de despliegue de LogiTrack: dev o prod."

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "El entorno debe sr dev o prod."
  }
}
