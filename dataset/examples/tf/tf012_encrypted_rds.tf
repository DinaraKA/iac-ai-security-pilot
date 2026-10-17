variable "db_password" {
  type      = string
  sensitive = true
}

resource "aws_db_instance" "example" {
  identifier          = "example-db"
  engine              = "mysql"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "example"
  password            = var.db_password
  storage_encrypted   = true
  skip_final_snapshot = true
}
