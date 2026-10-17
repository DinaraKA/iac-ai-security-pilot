resource "aws_s3_bucket_policy" "example" {
  bucket = "example-private-policy-bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "ScopedRead"
      Effect    = "Allow"
      Principal = {
        AWS = "arn:aws:iam::123456789012:role/example-reader"
      }
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::example-private-policy-bucket/*"]
    }]
  })
}
