resource "aws_ebs_volume" "example" {
  availability_zone = "us-east-1a"
  size              = 8
  encrypted         = true

  tags = {
    Name = "example-volume"
  }
}
