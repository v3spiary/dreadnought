variable "sel_domain_name" {
  description = "Selectel account number (domain name)"
  type        = string
  sensitive   = true
}

variable "sel_username" {
  description = "Selectel service user name"
  type        = string
}

variable "sel_password" {
  description = "Selectel service user password"
  type        = string
  sensitive   = true
}

variable "sel_auth_region" {
  description = "Selectel authentication region (e.g., ru-3, ru-9)"
  type        = string
  default     = "ru-9"
}

variable "sel_auth_url" {
  description = "Selectel authentication API URL"
  type        = string
  default     = "https://cloud.api.selcloud.ru/identity/v3/"
}

variable "sel_serv_user_id" {
  description = "Selectel service acc user id"
  type        = string
  sensitive   = true
}
