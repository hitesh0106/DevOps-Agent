variable "project_name" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "instance_class" { type = string; default = "db.t3.medium" }

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = var.subnet_ids
}

resource "aws_db_instance" "main" {
  identifier           = "${var.project_name}-${var.environment}"
  engine               = "postgres"
  engine_version       = "16.1"
  instance_class       = var.instance_class
  allocated_storage    = 20
  max_allocated_storage = 100
  db_name              = "devops_agent"
  username             = "agent"
  password             = "change-me-in-production"
  db_subnet_group_name = aws_db_subnet_group.main.name
  skip_final_snapshot  = true
  multi_az             = var.environment == "production"

  tags = { Name = "${var.project_name}-rds" }
}

output "endpoint" { value = aws_db_instance.main.endpoint }
output "db_name" { value = aws_db_instance.main.db_name }
