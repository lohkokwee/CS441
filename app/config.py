HOST = "localhost"
ROUTER_INT1_PORT = 8001
ROUTER_INT2_PORT = 8002
ROUTER_INT3_PORT = 8003
ROUTER_INT4_PORT = 8004
VPN_SERVER_PORT = 8005
ROUTER_INT5_PORT = 8006
PROTECTED_SERVER_PORT = 8007

DNS_SERVER_PREFIX = "0x3"

ROUTER_INT1_CONFIG = {
  "device_name": "Router",
  "network_int_ip_address": "0x11",
  "network_int_mac": "R1",
  "network_int_port": ROUTER_INT1_PORT,
  "max_connections": 5
}

NODE1_CONFIG = {
  "device_name": "Node",
  "node_mac": "N1",
  "network_int_mac": "R1", 
  "network_int_port": ROUTER_INT1_PORT,
  "dns_server_prefix": DNS_SERVER_PREFIX
}

ROUTER_INT2_CONFIG = {
  "device_name": "Router",
  "network_int_ip_address": "0x21",
  "network_int_mac": "R2",
  "network_int_port": ROUTER_INT2_PORT,
  "max_connections": 5,
  "network_int_relay_addresses": [(HOST, ROUTER_INT1_PORT)]
}

NODE2_CONFIG = {
  "device_name": "Node",
  "node_mac": "N2",
  "network_int_mac": "R2", 
  "network_int_port": ROUTER_INT2_PORT,
  "dns_server_prefix": DNS_SERVER_PREFIX
}

NODE3_CONFIG = {
  "device_name": "Node",
  "node_mac": "N3",
  "network_int_mac": "R2", 
  "network_int_port": ROUTER_INT2_PORT,
  "dns_server_prefix": DNS_SERVER_PREFIX,
  "malicious_dns_records": [
    {
      "domain_name": "N1.com",
      "ip_address": "0x2B"
    },
    {
      "domain_name": "abc.com",
      "ip_address": "0x2B"
    },
    {
      "domain_name": "def.com",
      "ip_address": "0x2B"
    }
  ]
}

ROUTER_INT3_CONFIG = {
  "device_name": "Router",
  "network_int_ip_address": "0x31",
  "network_int_mac": "R3",
  "network_int_port": ROUTER_INT3_PORT,
  "max_connections": 5,
  "network_int_relay_addresses": [(HOST, ROUTER_INT1_PORT), (HOST, ROUTER_INT2_PORT)],
}

DNS_SERVER_CONFIG = {
  "device_name": "DNS Server",
  "node_mac": "N4",
  "network_int_mac": "R3", 
  "network_int_port": ROUTER_INT3_PORT,
  "dns_records": [
    {
      "domain_name": "N1.com",
      "ip_address": "0x1A"
    }, {
      "domain_name": "www.N2.com",
      "ip_address": "0x2A"
    }, {
      "domain_name": "N3.com",
      "ip_address": "0x2B"
    }
  ]
}

ROUTER_INT4_CONFIG = {
  "device_name": "Router",
  "network_int_ip_address": "0x41",
  "network_int_mac": "R4",
  "network_int_port": ROUTER_INT4_PORT,
  "max_connections": 5,
  "network_int_relay_addresses": [(HOST, ROUTER_INT1_PORT), (HOST, ROUTER_INT2_PORT), (HOST, ROUTER_INT3_PORT)],
}

VPN_SERVER_CONFIG = {
  "device_name": "VPN Server",
  "network_int_ip_address": "0x51",
  "network_int_mac": "V1",
  "network_int_port": VPN_SERVER_PORT,
  "max_connections": 5,
  "network_int_relay_addresses": [(HOST, ROUTER_INT4_PORT)],
}

ROUTER_INT5_CONFIG = {
  "device_name": "Router",
  "network_int_ip_address": "0x61",
  "network_int_mac": "R5",
  "network_int_port": ROUTER_INT5_PORT,
  "max_connections": 5,
  "network_int_relay_addresses": [(HOST, ROUTER_INT1_PORT), (HOST, ROUTER_INT2_PORT), (HOST, ROUTER_INT3_PORT), (HOST, ROUTER_INT4_PORT)],
}

PROTECTED_SERVER_CONFIG = {
  "device_name": "Protected Server",
  "network_int_ip_address": "0x71",
  "network_int_mac": "P1",
  "network_int_port": PROTECTED_SERVER_PORT,
  "max_connections": 5,
  "network_int_relay_addresses": [(HOST, VPN_SERVER_PORT), (HOST, ROUTER_INT5_PORT)],
}

PROTECTED_NODE_CONFIG = {
  "device_name": "Protected Node",
  "node_mac": "P2",
  "network_int_mac": "P1", 
  "network_int_port": PROTECTED_SERVER_PORT,
  "dns_server_prefix": DNS_SERVER_PREFIX
}