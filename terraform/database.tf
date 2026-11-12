resource "aws_db_subnet_group" "arteco" {
  count      = var.enable_database ? 1 : 0
  name       = "${var.project_name}-${var.environment}-db-subnets"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

resource "aws_security_group" "database" {
  count       = var.enable_database ? 1 : 0
  name        = "${var.project_name}-${var.environment}-database-sg"
  description = "PostgreSQL solo desde las funciones Lambda de ARTECO"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL desde Lambda"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.lambda_sg.id]
  }
}

resource "aws_rds_cluster" "arteco" {
  count                           = var.enable_database ? 1 : 0
  cluster_identifier              = "${var.project_name}-${var.environment}"
  engine                          = "aurora-postgresql"
  engine_mode                     = "provisioned"
  database_name                   = var.database_name
  master_username                 = "arteco_admin"
  manage_master_user_password     = true
  storage_encrypted               = true
  backup_retention_period         = 7
  preferred_backup_window         = "03:00-04:00"
  db_subnet_group_name            = aws_db_subnet_group.arteco[0].name
  vpc_security_group_ids          = [aws_security_group.database[0].id]
  enabled_cloudwatch_logs_exports = ["postgresql"]
  deletion_protection             = true
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${var.project_name}-${var.environment}-final"

  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 2
  }
}

resource "aws_rds_cluster_instance" "arteco" {
  count               = var.enable_database ? 1 : 0
  identifier          = "${var.project_name}-${var.environment}-01"
  cluster_identifier  = aws_rds_cluster.arteco[0].id
  instance_class      = "db.serverless"
  engine              = aws_rds_cluster.arteco[0].engine
  publicly_accessible = false
}
