variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-2"
}

variable "db_password" {
  description = "RDS root user password"
  sensitive   = true
}
