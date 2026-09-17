variable "aws_region" {
  description = "Regiao AWS onde os recursos serao criados"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Nome do bucket S3 para armazenar os dados financeiros (deve ser globalmente unico)"
  type        = string
}

variable "environment" {
  description = "Nome do ambiente (usado em tags)"
  type        = string
  default     = "dev"
}

variable "dashboard_bucket_name" {
  description = "Nome do bucket S3 que hospeda o dashboard estatico (deve ser globalmente unico)"
  type        = string
}
