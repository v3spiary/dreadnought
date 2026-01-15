resource "selectel_vpc_keypair_v2" "keypair_1" {
  name       = "keypair"
  public_key = file("~/.ssh/id_rsa.pub")
  user_id    = var.sel_serv_user_id
}

resource "openstack_compute_flavor_v2" "flavor_1" {
  name      = "deadwood-flavor-with-network-volume"
  vcpus     = 2
  ram       = 2048
  disk      = 0
  is_public = false

  lifecycle {
    create_before_destroy = true
  }
}

resource "openstack_networking_port_v2" "port_web" {
  name       = "port-web"
  network_id = openstack_networking_network_v2.network_1.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet_1.id
  }
}

resource "openstack_blockstorage_volume_v3" "volume_web_boot" {
  name                 = "boot-volume-for-web"
  size                 = "5"
  image_id             = data.openstack_images_image_v2.image_1.id
  volume_type          = "fast.ru-9a"
  availability_zone    = "ru-9a"
  enable_online_resize = true

  lifecycle {
    ignore_changes = [image_id]
  }
}

resource "openstack_blockstorage_volume_v3" "volume_web_additional" {
  name                 = "additional-volume-for-web"
  size                 = "7"
  volume_type          = "universal.ru-9a"
  availability_zone    = "ru-9a"
  enable_online_resize = true
}

resource "openstack_compute_instance_v2" "server_web" {
  name              = "deadwood_web"
  flavor_id         = openstack_compute_flavor_v2.flavor_1.id
  key_pair          = selectel_vpc_keypair_v2.keypair_1.name
  availability_zone = "ru-9a"

  network {
    port = openstack_networking_port_v2.port_web.id
  }

  lifecycle {
    ignore_changes = [image_id]
  }

  block_device {
    uuid             = openstack_blockstorage_volume_v3.volume_web_boot.id
    source_type      = "volume"
    destination_type = "volume"
    boot_index       = 0
  }

  block_device {
    uuid             = openstack_blockstorage_volume_v3.volume_web_additional.id
    source_type      = "volume"
    destination_type = "volume"
    boot_index       = -1
  }

  vendor_options {
    ignore_resize_confirmation = true
  }
}

resource "openstack_networking_floatingip_v2" "floatingip_web" {
  pool = "external-network"
}

resource "openstack_networking_floatingip_associate_v2" "association_web" {
  port_id     = openstack_networking_port_v2.port_web.id
  floating_ip = openstack_networking_floatingip_v2.floatingip_web.address
}

output "public_ip_address_web" {
  value = openstack_networking_floatingip_v2.floatingip_web.fixed_ip
}
