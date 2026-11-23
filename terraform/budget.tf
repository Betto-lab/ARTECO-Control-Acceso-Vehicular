resource "aws_budgets_budget" "dev_monthly" {
  count = var.enable_cost_budget && var.environment == "dev" ? 1 : 0

  name         = var.cost_budget_name
  budget_type  = "COST"
  limit_amount = tostring(var.cost_budget_limit_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = var.cost_budget_alert_threshold
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.cost_budget_notification_email]
  }
}
