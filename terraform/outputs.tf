output "api_url" {
  description = "URL publica del API Gateway"
  value       = aws_apigatewayv2_api.http_api.api_endpoint
}

output "upload_endpoint" {
  description = "Endpoint POST para cargar archivos"
  value       = "${aws_apigatewayv2_api.http_api.api_endpoint}/upload"
}

output "bucket_name" {
  description = "Nombre del bucket S3"
  value       = aws_s3_bucket.files.bucket
}

output "sqs_queue_url" {
  description = "URL de la cola principal SQS"
  value       = aws_sqs_queue.main.url
}

output "dlq_url" {
  description = "URL de la Dead Letter Queue"
  value       = aws_sqs_queue.dlq.url
}

output "upload_lambda_name" {
  value = aws_lambda_function.upload.function_name
}

output "processor_lambda_name" {
  value = aws_lambda_function.processor.function_name
}