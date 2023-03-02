LOCALHOST = "localhost"
ROUTER1_PORT = 8001
ROUTER2_PORT = 8002

NODE1_PORT = 8101
NODE2_PORT = 8102
NODE3_PORT = 8103

ROUTER1_CONFIG = {
  "router_ip_address": "0x11",
  "router_mac": "R1",
  "router_port": ROUTER1_PORT,
  "max_connections": 5
}

NODE1_CONFIG = {
  "node_mac": "N1",
  "router_mac": "R1", 
  "router_port": ROUTER1_PORT
}

ROUTER2_CONFIG = {
  "router_ip_address": "0x21",
  "router_mac": "R2",
  "router_port": ROUTER2_PORT,
  "max_connections": 5,
  "router_relay_addresses": [(LOCALHOST, ROUTER1_PORT)]
}

NODE2_CONFIG = {
  "node_mac": "N2",
  "router_mac": "R2", 
  "router_port": ROUTER2_PORT
}

NODE3_CONFIG = {
  "node_mac": "N3",
  "router_mac": "R2", 
  "router_port": ROUTER2_PORT
}