resource "openstack_networking_port_v2" "port_ai" {
  name       = "port-ai"
  network_id = openstack_networking_network_v2.network_1.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet_1.id
  }
}

resource "openstack_blockstorage_volume_v3" "volume_ai_boot" {
  name                 = "boot-volume-for-ai"
  size                 = "5"
  image_id             = data.openstack_images_image_v2.image_1.id
  volume_type          = "fast.ru-9a"
  availability_zone    = "ru-9a"
  enable_online_resize = true

  lifecycle {
    ignore_changes = [image_id]
  }
}

resource "openstack_compute_instance_v2" "server_ai" {
  name              = "deadwood_ai"
  flavor_id         = "3042"
  key_pair          = selectel_vpc_keypair_v2.keypair_1.name
  availability_zone = "ru-9a"

  network {
    port = openstack_networking_port_v2.port_ai.id
  }

  lifecycle {
    ignore_changes = [image_id]
  }

  block_device {
    uuid             = openstack_blockstorage_volume_v3.volume_ai_boot.id
    source_type      = "volume"
    destination_type = "volume"
    boot_index       = 0
  }

  vendor_options {
    ignore_resize_confirmation = true
  }
}

resource "openstack_networking_floatingip_v2" "floatingip_ai" {
  pool = "external-network"
}

resource "openstack_networking_floatingip_associate_v2" "association_ai" {
  port_id     = openstack_networking_port_v2.port_ai.id
  floating_ip = openstack_networking_floatingip_v2.floatingip_ai.address
}

output "public_ip_address_ai" {
  value = openstack_networking_floatingip_v2.floatingip_ai.fixed_ip
}
