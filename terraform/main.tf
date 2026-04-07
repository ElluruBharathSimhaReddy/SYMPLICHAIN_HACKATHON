terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "frontend_assets" {
  bucket = var.frontend_bucket_name
}

resource "aws_instance" "app_server" {
  ami           = var.ec2_ami
  instance_type = var.instance_type
  tags = {
    Name = "symflow-app"
  }
}
