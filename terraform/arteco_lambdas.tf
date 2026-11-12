locals {
  arteco_lambdas = {
    vehicle_access      = "vehicle_access"
    plate_recognition   = "plate_recognition"
    face_verification   = "face_verification"
    access_registration = "access_registration"
    alerts              = "alerts"
  }
}

data "archive_file" "arteco" {
  for_each    = local.arteco_lambdas
  type        = "zip"
  source_file = "${path.module}/../lambda/${each.value}/index.py"
  output_path = "${path.module}/${each.key}.zip"
}

resource "aws_iam_role" "arteco_lambda" {
  name               = "${var.project_name}-${var.environment}-arteco-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "arteco_basic" {
  role       = aws_iam_role.arteco_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "arteco_vpc" {
  role       = aws_iam_role.arteco_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_policy" "arteco_runtime" {
  name = "${var.project_name}-${var.environment}-arteco-runtime"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      jsondecode(data.aws_iam_policy_document.arteco_ai.json).Statement,
      [{ Effect = "Allow", Action = ["sqs:SendMessage"], Resource = aws_sqs_queue.main.arn }],
      [{ Effect = "Allow", Action = ["sns:Publish"], Resource = aws_sns_topic.alerts.arn }]
    )
  })
}

resource "aws_iam_role_policy_attachment" "arteco_runtime" {
  role       = aws_iam_role.arteco_lambda.name
  policy_arn = aws_iam_policy.arteco_runtime.arn
}

resource "aws_lambda_function" "arteco" {
  for_each         = local.arteco_lambdas
  function_name    = "${var.project_name}-${var.environment}-${replace(each.key, "_", "-")}"
  filename         = data.archive_file.arteco[each.key].output_path
  source_code_hash = data.archive_file.arteco[each.key].output_base64sha256
  role             = aws_iam_role.arteco_lambda.arn
  handler          = "index.lambda_handler"
  runtime          = "python3.12"
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      EVIDENCE_BUCKET  = aws_s3_bucket.files.bucket
      ACCESS_QUEUE_URL = aws_sqs_queue.main.url
      ALERTS_TOPIC_ARN = aws_sns_topic.alerts.arn
    }
  }

  vpc_config {
    subnet_ids         = [aws_subnet.private_a.id, aws_subnet.private_b.id]
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  depends_on = [aws_iam_role_policy_attachment.arteco_basic, aws_iam_role_policy_attachment.arteco_vpc, aws_iam_role_policy_attachment.arteco_runtime]
}

resource "aws_apigatewayv2_integration" "vehicle_access" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.arteco["vehicle_access"].invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.http_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.web.id]
    issuer   = "https://${aws_cognito_user_pool.arteco.endpoint}"
  }
}

resource "aws_apigatewayv2_route" "vehicle_access" {
  api_id             = aws_apigatewayv2_api.http_api.id
  route_key          = "POST /vehicle-access"
  target             = "integrations/${aws_apigatewayv2_integration.vehicle_access.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_lambda_permission" "vehicle_access_api" {
  statement_id  = "AllowVehicleAccessAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.arteco["vehicle_access"].function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
