
terraform {
  backend "s3" {
    bucket       = "arteco-tfstate-2026-48271"
    key          = "arteco/dev/terraform.tfstate"
    region       = "us-east-2"
    encrypt      = true
    use_lockfile = true
  }
}
