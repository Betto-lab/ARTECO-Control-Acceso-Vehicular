locals {
  database_schedule_enabled = var.enable_database && var.enable_database_schedule && var.environment != "prod"
}

data "aws_iam_policy_document" "database_scheduler_assume" {
  count = local.database_schedule_enabled ? 1 : 0

  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "database_scheduler" {
  count              = local.database_schedule_enabled ? 1 : 0
  name               = "${var.project_name}-${var.environment}-database-scheduler"
  assume_role_policy = data.aws_iam_policy_document.database_scheduler_assume[0].json
}

data "aws_iam_policy_document" "database_scheduler" {
  count = local.database_schedule_enabled ? 1 : 0

  statement {
    actions = [
      "rds:StartDBCluster",
      "rds:StopDBCluster"
    ]
    resources = [aws_rds_cluster.arteco[0].arn]
  }
}

resource "aws_iam_role_policy" "database_scheduler" {
  count  = local.database_schedule_enabled ? 1 : 0
  name   = "database-start-stop"
  role   = aws_iam_role.database_scheduler[0].id
  policy = data.aws_iam_policy_document.database_scheduler[0].json
}

resource "aws_scheduler_schedule" "database_start" {
  count = local.database_schedule_enabled ? 1 : 0
  name  = "${var.project_name}-${var.environment}-database-start"

  schedule_expression          = var.database_start_schedule
  schedule_expression_timezone = var.database_schedule_timezone

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:rds:startDBCluster"
    role_arn = aws_iam_role.database_scheduler[0].arn
    input = jsonencode({
      DbClusterIdentifier = aws_rds_cluster.arteco[0].cluster_identifier
    })
  }
}

resource "aws_scheduler_schedule" "database_stop" {
  count = local.database_schedule_enabled ? 1 : 0
  name  = "${var.project_name}-${var.environment}-database-stop"

  schedule_expression          = var.database_stop_schedule
  schedule_expression_timezone = var.database_schedule_timezone

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:rds:stopDBCluster"
    role_arn = aws_iam_role.database_scheduler[0].arn
    input = jsonencode({
      DbClusterIdentifier = aws_rds_cluster.arteco[0].cluster_identifier
    })
  }
}
