resource "aws_sqs_queue" "dlq" {
  name = "${var.project_name}-${var.environment}-dlq"

  message_retention_seconds = 1209600

  tags = {
    Name = "${var.project_name}-${var.environment}-dlq"
  }
}

resource "aws_sqs_queue" "main" {
  name = "${var.project_name}-${var.environment}-queue"

  visibility_timeout_seconds = 180

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.project_name}-${var.environment}-queue"
  }
}