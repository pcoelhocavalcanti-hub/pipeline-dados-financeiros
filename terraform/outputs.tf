output "bucket_name" {
  description = "Nome do bucket S3 criado"
  value       = aws_s3_bucket.dados_financeiros.id
}

output "bucket_arn" {
  description = "ARN do bucket S3 criado"
  value       = aws_s3_bucket.dados_financeiros.arn
}

output "bucket_region" {
  description = "Regiao do bucket S3 criado"
  value       = var.aws_region
}
