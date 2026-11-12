resource "aws_cognito_user_pool" "arteco" {
  name                     = "${var.project_name}-${var.environment}-users"
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length                   = 12
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 3
  }

  mfa_configuration = "OPTIONAL"
  software_token_mfa_configuration { enabled = true }
}

resource "aws_cognito_user_pool_client" "web" {
  name                                 = "${var.project_name}-${var.environment}-web"
  user_pool_id                         = aws_cognito_user_pool.arteco.id
  generate_secret                      = false
  prevent_user_existence_errors        = "ENABLED"
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email"]
  callback_urls                        = ["http://localhost:8080"]
  supported_identity_providers         = ["COGNITO"]
}
