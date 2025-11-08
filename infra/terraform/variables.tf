variable "aws_region" {
  description = "La región de AWS donde se desplegarán los recursos."
  type        = string
  default     = "us-east-1"
}

variable "vector_index_bucket" {
  description = "El nombre del bucket de S3 que contiene el índice de vectores."
  type        = string
  default     = "lol-wrapped-vector-index"
}

variable "vector_index_name" {
  description = "El nombre del índice de vectores dentro del bucket."
  type        = string
  default     = "lol-wrapped-index"
}

variable "app_name" {
  description = "El nombre de la aplicación, usado para nombrar recursos."
  type        = string
  default     = "lol-wrapped-rag-agent"
}


