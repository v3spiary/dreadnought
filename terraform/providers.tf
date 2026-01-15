terraform {
  required_providers {
    selectel  = {
      source  = "selectel/selectel"
      version = "~> 6.0"
    }
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "2.1.0"
    }
  }
}

provider "selectel" {
  domain_name = var.sel_domain_name
  username    = var.sel_username
  password    = var.sel_password
  auth_region = var.sel_auth_region
  auth_url    = var.sel_auth_url
}

resource "selectel_vpc_project_v2" "project_deadwood" {
  name = "deadwood"
}

provider "openstack" {
  auth_url    = "https://cloud.api.selcloud.ru/identity/v3"
  domain_name = var.sel_domain_name
  tenant_id   = selectel_vpc_project_v2.project_deadwood.id
  user_name   = var.sel_username
  password    = var.sel_password
  region      = var.sel_auth_region
}
