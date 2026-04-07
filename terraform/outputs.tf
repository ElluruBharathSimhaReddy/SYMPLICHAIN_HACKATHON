output "app_server_id" {
  value = aws_instance.app_server.id
}

output "frontend_bucket" {
  value = aws_s3_bucket.frontend_assets.bucket
}
