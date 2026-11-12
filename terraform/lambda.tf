data "archive_file" "upload_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/upload/index.py"
  output_path = "${path.module}/upload_lambda.zip"
}

data "archive_file" "processor_lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/processor/index.py"
  output_path = "${path.module}/processor_lambda.zip"
}

resource "aws_security_group" "lambda_sg" {
  name        = "${var.project_name}-${var.environment}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-lambda-sg"
  }
}

resource "aws_lambda_function" "upload" {
  function_name = "${var.project_name}-${var.environment}-upload"

  filename         = data.archive_file.upload_lambda_zip.output_path
  source_code_hash = data.archive_file.upload_lambda_zip.output_base64sha256

  role    = aws_iam_role.upload_lambda_role.arn
  handler = "index.lambda_handler"
  runtime = "python3.12"

  timeout     = 30
  memory_size = 256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.files.bucket
      QUEUE_URL   = aws_sqs_queue.main.url
    }
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_group_ids = [
      aws_security_group.lambda_sg.id
    ]
  }

  depends_on = [
    aws_iam_role_policy_attachment.upload_basic_execution,
    aws_iam_role_policy_attachment.upload_vpc_access,
    aws_iam_role_policy_attachment.upload_custom
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-upload"
  }
}

resource "aws_lambda_function" "processor" {
  function_name = "${var.project_name}-${var.environment}-processor"

  filename         = data.archive_file.processor_lambda_zip.output_path
  source_code_hash = data.archive_file.processor_lambda_zip.output_base64sha256

  role    = aws_iam_role.processor_lambda_role.arn
  handler = "index.lambda_handler"
  runtime = "python3.12"

  timeout     = 60
  memory_size = 256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.files.bucket
    }
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.private_a.id,
      aws_subnet.private_b.id
    ]

    security_group_ids = [
      aws_security_group.lambda_sg.id
    ]
  }

  depends_on = [
    aws_iam_role_policy_attachment.processor_basic_execution,
    aws_iam_role_policy_attachment.processor_vpc_access,
    aws_iam_role_policy_attachment.processor_custom
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-processor"
  }
}

resource "aws_lambda_event_source_mapping" "sqs_processor" {
  event_source_arn = aws_sqs_queue.main.arn
  function_name    = aws_lambda_function.processor.arn

  batch_size = 1

  enabled = true
}