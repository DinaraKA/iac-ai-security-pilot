resource "aws_security_group" "example" {
  name        = "synthetic-restricted-ssh"
  description = "Synthetic negative-control example; do not deploy"
  ingress {
    description = "Restricted to documentation-only example range"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.0.2.10/32"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
