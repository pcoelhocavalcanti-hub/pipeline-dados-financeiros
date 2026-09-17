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

output "lambda_function_name" {
  description = "Nome da funcao Lambda de coleta diaria"
  value       = aws_lambda_function.coleta_diaria.function_name
}

output "eventbridge_rule_name" {
  description = "Nome da regra do EventBridge que dispara a coleta diaria"
  value       = aws_cloudwatch_event_rule.coleta_diaria.name
}

output "dashboard_url" {
  description = "URL publica do dashboard estatico"
  value       = aws_s3_bucket_website_configuration.dashboard.website_endpoint
}
