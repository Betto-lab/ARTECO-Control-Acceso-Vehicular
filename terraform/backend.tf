
terraform {
  backend "s3" {
    bucket       = "arteco-tfstate-2026-48271"
    region       = "us-east-2"
    encrypt      = true
    use_lockfile = true
  }
}
