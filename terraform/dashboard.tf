# Bucket separado do bucket de dados (que continua privado). Este aqui hospeda
# o dashboard estatico (dashboard/index.html) como um site S3 publico.

resource "aws_s3_bucket" "dashboard" {
  bucket = var.dashboard_bucket_name

  tags = {
    Project     = "pipeline-dados-financeiros"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "dashboard" {
  bucket = aws_s3_bucket.dashboard.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "dashboard" {
  bucket = aws_s3_bucket.dashboard.id

  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_policy" "dashboard_public_read" {
  bucket = aws_s3_bucket.dashboard.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicReadGetObject"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.dashboard.arn}/*"
    }]
  })

  # A policy so pode ser aplicada depois que o bloqueio de acesso publico
  # for liberado, senao a API da AWS rejeita.
  depends_on = [aws_s3_bucket_public_access_block.dashboard]
}

resource "aws_s3_object" "dashboard_index" {
  bucket       = aws_s3_bucket.dashboard.id
  key          = "index.html"
  source       = "${path.module}/../dashboard/index.html"
  etag         = filemd5("${path.module}/../dashboard/index.html")
  content_type = "text/html"
}
