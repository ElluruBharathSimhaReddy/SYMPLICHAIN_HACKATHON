variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "frontend_bucket_name" {
  type = string
}

variable "ec2_ami" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}
