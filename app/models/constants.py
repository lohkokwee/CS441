LOCALHOST = "localhost"
ROUTER_INT1_PORT = 8001
ROUTER_INT2_PORT = 8002

NODE1_PORT = 8101
NODE2_PORT = 8102
NODE3_PORT = 8103

ROUTER_INT1_CONFIG = {
  "router_int_ip_address": "0x11",
  "router_int_mac": "R1",
  "router_int_port": ROUTER_INT1_PORT,
  "max_connections": 5
}

NODE1_CONFIG = {
  "node_mac": "N1",
  "router_int_mac": "R1", 
  "router_int_port": ROUTER_INT1_PORT
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
  "router_int_port": ROUTER_INT2_PORT
}

NODE3_CONFIG = {
  "node_mac": "N3",
  "router_int_mac": "R2", 
  "router_int_port": ROUTER_INT2_PORT
}