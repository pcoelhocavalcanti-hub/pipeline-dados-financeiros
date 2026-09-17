# Lambda que roda a coleta (acoes + Selic) e sobe os CSVs direto pro S3,
# disparada diariamente pelo EventBridge. Substitui a execucao manual dos
# scripts em scripts/ para o fluxo automatizado.

resource "aws_s3_object" "lambda_package" {
  bucket = aws_s3_bucket.dados_financeiros.id
  key    = "lambda-artifacts/lambda_function.zip"
  source = "${path.module}/../lambda/build.zip"
  etag   = filemd5("${path.module}/../lambda/build.zip")
}

resource "aws_iam_role" "lambda_exec" {
  name = "pipeline-financeiro-lambda-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_s3_write" {
  name = "pipeline-financeiro-lambda-s3-write"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["s3:PutObject"]
      Resource = [
        "${aws_s3_bucket.dados_financeiros.arn}/acoes/*",
        "${aws_s3_bucket.dados_financeiros.arn}/selic/*",
      ]
    }]
  })
}

resource "aws_lambda_function" "coleta_diaria" {
  function_name = "pipeline-financeiro-coleta-diaria"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 512

  s3_bucket        = aws_s3_bucket.dados_financeiros.id
  s3_key           = aws_s3_object.lambda_package.key
  source_code_hash = filebase64sha256("${path.module}/../lambda/build.zip")

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.dados_financeiros.id
    }
  }
}

resource "aws_cloudwatch_event_rule" "coleta_diaria" {
  name = "pipeline-financeiro-coleta-diaria"
  # 21:00 UTC = 18:00 horario de Brasilia (UTC-3), apos o fechamento do
  # pregao (B3 fecha as 18h). Roda so em dias uteis.
  schedule_expression = "cron(0 21 ? * MON-FRI *)"
}

resource "aws_cloudwatch_event_target" "coleta_diaria" {
  rule = aws_cloudwatch_event_rule.coleta_diaria.name
  arn  = aws_lambda_function.coleta_diaria.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.coleta_diaria.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.coleta_diaria.arn
}
