resource "aws_s3_bucket_policy" "example" {
  bucket = "example-public-policy-bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "PublicRead"
      Effect    = "Allow"
      Principal = "*"
      Action    = ["s3:GetObject"]
      Resource  = ["arn:aws:s3:::example-public-policy-bucket/*"]
    }]
  })
}
