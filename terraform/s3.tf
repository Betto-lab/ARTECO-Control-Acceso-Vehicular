resource "aws_s3_bucket" "files" {
  bucket        = "${var.project_name}-${var.environment}-files-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = {
    Name = "${var.project_name}-${var.environment}-files"
  }
}

resource "aws_s3_bucket_public_access_block" "files" {
  bucket = aws_s3_bucket.files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "files" {
  bucket = aws_s3_bucket.files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "files" {
  bucket = aws_s3_bucket.files.id

  versioning_configuration {
    status = "Enabled"
  }
}

locals {
  file_lifecycle_by_environment = {
    dev = {
      standard_ia_days = 30
      glacier_days     = 90
      expiration_days  = 365
    }
    qa = {
      standard_ia_days = 30
      glacier_days     = 90
      expiration_days  = 365
    }
    prod = {
      standard_ia_days = 60
      glacier_days     = 180
      expiration_days  = 730
    }
  }

  file_lifecycle = local.file_lifecycle_by_environment[var.environment]
}

resource "aws_s3_bucket_lifecycle_configuration" "files" {
  bucket = aws_s3_bucket.files.id

  depends_on = [aws_s3_bucket_versioning.files]

  rule {
    id     = "optimize-large-uploads"
    status = "Enabled"

    filter {
      and {
        prefix                   = "uploads/"
        object_size_greater_than = 131072
      }
    }

    transition {
      days          = local.file_lifecycle.standard_ia_days
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = local.file_lifecycle.glacier_days
      storage_class = "GLACIER"
    }

    expiration {
      days = local.file_lifecycle.expiration_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
