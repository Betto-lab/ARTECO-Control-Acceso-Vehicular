data "aws_iam_policy_document" "arteco_ai" {
  statement {
    sid       = "ReadEvidence"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.files.arn}/evidence/*"]
  }

  statement {
    sid       = "AnalyzeEvidence"
    actions   = ["rekognition:DetectText", "rekognition:CompareFaces"]
    resources = ["*"]
  }
}

# Rekognition DetectText y CompareFaces no requieren un recurso persistente.
# Las funciones consumen imágenes privadas de S3 y reciben permisos mínimos arriba.
