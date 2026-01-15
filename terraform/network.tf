resource "openstack_networking_network_v2" "network_1" {
  name           = "private-network"
  admin_state_up = "true"

  depends_on = [
    selectel_vpc_project_v2.project_deadwood
  ]
}

resource "openstack_networking_subnet_v2" "subnet_1" {
  network_id = openstack_networking_network_v2.network_1.id
  cidr       = "192.168.199.0/24"

  depends_on = [
    selectel_vpc_project_v2.project_deadwood
  ]
}

data "openstack_networking_network_v2" "external_network_1" {
  external = true

  depends_on = [
    selectel_vpc_project_v2.project_deadwood
  ]
}

resource "openstack_networking_router_v2" "router_1" {
  name                = "router"
  external_network_id = data.openstack_networking_network_v2.external_network_1.id
}

resource "openstack_networking_router_interface_v2" "router_interface_1" {
  router_id = openstack_networking_router_v2.router_1.id
  subnet_id = openstack_networking_subnet_v2.subnet_1.id
}

data "openstack_images_image_v2" "image_1" {
  name        = "Ubuntu 22.04 LTS 64-bit"
  most_recent = true
  visibility  = "public"

  depends_on = [
    selectel_vpc_project_v2.project_deadwood
  ]
}
