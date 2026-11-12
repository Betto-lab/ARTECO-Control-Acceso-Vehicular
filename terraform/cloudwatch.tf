resource "aws_cloudwatch_log_group" "upload_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.upload.function_name}"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-upload-logs"
  }
}

resource "aws_cloudwatch_log_group" "processor_lambda" {
  name              = "/aws/lambda/${aws_lambda_function.processor.function_name}"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-processor-logs"
  }
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.project_name}-${var.environment}"
  retention_in_days = 7

  tags = {
    Name = "${var.project_name}-${var.environment}-api-logs"
  }
}

resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name        = "${var.project_name}-${var.environment}-dlq-messages"
  alarm_description = "Alarma cuando existen mensajes en la Dead Letter Queue"

  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  statistic           = "Average"
  period              = 60
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"

  dimensions = {
    QueueName = aws_sqs_queue.dlq.name
  }

  treat_missing_data = "notBreaching"

  tags = {
    Name = "${var.project_name}-${var.environment}-dlq-alarm"
  }
}