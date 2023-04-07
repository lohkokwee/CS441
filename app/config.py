LOCALHOST = "localhost"
ROUTER_INT1_PORT = 8001
ROUTER_INT2_PORT = 8002
ROUTER_INT3_PORT = 8003

DNS_SERVER_PREFIX = "0x3"

ROUTER_INT1_CONFIG = {
  "router_int_ip_address": "0x11",
  "router_int_mac": "R1",
  "router_int_port": ROUTER_INT1_PORT,
  "max_connections": 5
}

NODE1_CONFIG = {
  "node_mac": "N1",
  "router_int_mac": "R1", 
  "router_int_port": ROUTER_INT1_PORT,
  "dns_server_prefix": DNS_SERVER_PREFIX
}

ROUTER_INT2_CONFIG = {
  "router_int_ip_address": "0x21",
  "router_int_mac": "R2",
  "router_int_port": ROUTER_INT2_PORT,
  "max_connections": 5,
  "router_int_relay_addresses": [(LOCALHOST, ROUTER_INT1_PORT)]
}

NODE2_CONFIG = {
  "node_mac": "N2",
  "router_int_mac": "R2", 
  "router_int_port": ROUTER_INT2_PORT,
  "dns_server_prefix": DNS_SERVER_PREFIX
}

NODE3_CONFIG = {
  "node_mac": "N3",
  "router_int_mac": "R2", 
  "router_int_port": ROUTER_INT2_PORT,
  "dns_server_prefix": DNS_SERVER_PREFIX
}

ROUTER_INT3_CONFIG = {
  "router_int_ip_address": "0x31",
  "router_int_mac": "R3",
  "router_int_port": ROUTER_INT3_PORT,
  "max_connections": 5,
  "router_int_relay_addresses": [(LOCALHOST, ROUTER_INT1_PORT), (LOCALHOST, ROUTER_INT2_PORT)],
}

DNS_SERVER_CONFIG = {
  "node_mac": "N4",
  "router_int_mac": "R3", 
  "router_int_port": ROUTER_INT3_PORT,
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