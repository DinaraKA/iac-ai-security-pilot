resource "aws_security_group" "example" {
  name        = "synthetic-open-ssh"
  description = "Synthetic research example; do not deploy"
  ingress {
    description = "Intentionally insecure test case"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
