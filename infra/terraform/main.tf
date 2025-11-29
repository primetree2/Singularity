terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.region
  # TODO: configure provider credentials (environment variables, shared config, or assumed role)
}

variable "region" {
  type    = string
  default = "us-east-1"
}

####################
# Networking (VPC)
####################
# TODO: Replace this simple VPC with a production-ready design (subnets, NAT, route tables, ACLs)
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "singularity-vpc"
  }
}

####################
# RDS (PostgreSQL)
####################
# TODO: Harden this RDS instance (multi-AZ, backups, parameter groups, subnet groups, security groups)
variable "db_name" {
  type    = string
  default = "singularity"
}

variable "db_username" {
  type    = string
  default = "postgres"
}

variable "db_password" {
  type    = string
  default = "changeme" # TODO: replace with secure secret via TF var or secret manager
}

resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  name                 = var.db_name
  username             = var.db_username
  password             = var.db_password
  skip_final_snapshot  = true
  publicly_accessible  = false

  # TODO: attach to subnet group and proper security groups
  tags = {
    Name = "singularity-postgres"
  }
}

####################
# ElastiCache (Redis)
####################
# TODO: Configure subnet group, parameter group, and security group for production
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "singularity-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"

  tags = {
    Name = "singularity-redis"
  }
}

####################
# Compute (ECS cluster placeholder)
####################
# TODO: Replace with ECS Fargate / EKS / EC2 autoscaling and proper task definitions
resource "aws_ecs_cluster" "api_cluster" {
  name = "singularity-api-cluster"
}

# Example ECS service (placeholder)
# NOTE: This resource requires task_definition and other configs - adjust for actual deployment
resource "aws_ecs_service" "api_service" {
  name            = "singularity-api-service"
  cluster         = aws_ecs_cluster.api_cluster.id
  launch_type     = "FARGATE"
  desired_count   = 1
  # TODO: attach to a proper task_definition (aws_ecs_task_definition)
  # task_definition = aws_ecs_task_definition.api_task.arn

  # The following is intentionally minimal; flesh out networking and task defs for production
  network_configuration {
    subnets         = [] # TODO: provide subnet ids
    security_groups = [] # TODO: provide security group ids
  }

  tags = {
    Name = "singularity-api-service"
  }
}

####################
# S3 (Static assets / web)
####################
# TODO: Configure bucket policy, website hosting, versioning, and lifecycle rules as needed
resource "aws_s3_bucket" "web_assets" {
  bucket = "singularity-web-assets-${random_id.suffix.hex}"
  acl    = "private"

  tags = {
    Name = "singularity-web-assets"
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}

####################
# Outputs
####################
output "vpc_id" {
  value = aws_vpc.main.id
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.address
  description = "Postgres endpoint for database access (use with proper security group rules)"
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "s3_bucket" {
  value = aws_s3_bucket.web_assets.id
}

####################
# Notes
####################
# - This is a minimal, placeholder Terraform configuration intended to provide structure.
# - TODO: Add networking (subnets, NAT, IGW), security groups, IAM roles, logging, monitoring, and backups.
# - TODO: Move secrets (db password, etc.) to a secure secret manager (AWS Secrets Manager, SSM Parameter Store).
# - TODO: Add modules for repeatable, testable infrastructure (VPC module, RDS module, ECS module).
