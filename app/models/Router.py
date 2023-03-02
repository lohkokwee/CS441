import socket
import time
import threading

class Router:
  router_address = None
  router_ip_address = None
  router_mac = None
  router_socket = None

  router_relay = {}

  max_connections = 0
  arp_table_socket = {}
  arp_table_mac = {}

  def __init__(
    self,
    router_ip_address: str,
    router_mac: str,
    router_port: int,
    max_connections: int,
    router_relay: list = {},
    router_host: str = "localhost"
  ):
    self.router_address = (router_host, router_port)
    self.router_ip_address = router_ip_address
    self.router_mac = router_mac
    self.max_connections = max_connections

    self.router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.router_socket.bind(self.router_address)

  def get_available_ip_address(self):
    for i in range(self.max_connections):
      check_ip = self.router_ip_address[:-1] + chr(ord('A') + i)
      if (not check_ip in self.arp_table_mac):
        return check_ip
    return False

  def assign_ip_addess(self, node_socket: socket.socket) -> str:
    assigned_ip_address = self.get_available_ip_address()
    node_socket.send(bytes("assign_ip_address" ,"utf-8"))
    time.sleep(1)
    node_socket.send(bytes(f"{assigned_ip_address}" ,"utf-8"))
    time.sleep(1)
    node_socket.send(bytes("assign_ip_address_completed" ,"utf-8"))
    time.sleep(1)
    return assigned_ip_address

  def request_mac_address(self, node_socket: socket.socket) -> str:
    node_socket.send(bytes("request_mac_address" ,"utf-8"))
    while True:
      message = node_socket.recv(1024).decode("utf-8")
      if (message == "request_mac_address_completed"):
        break
      response_mac_address = message
    
    return response_mac_address

  def build_arp_table(self, ip_address:str, mac_address: str, node_socket: socket.socket) -> None:
    self.arp_table_mac[ip_address] = mac_address
    self.arp_table_socket[ip_address] = node_socket
    return 

  def connection_request(self, node_socket: socket.socket):
    '''
      Establishes arp tables for socket and mac.
      1. Assign free IP address.
      2. Request MAC address.
    '''
    print(f"Connection request received.")
    print(f"Updating ARP tables...")
    
    print(f"Assigning free IP address... [1/3]")
    assigned_ip_address = self.assign_ip_addess(node_socket)

    print(f"Requesting MAC address... [2/3]")
    response_mac_address = self.request_mac_address(node_socket)

    print(f"Building ARP tables... [3/3]")
    self.build_arp_table(assigned_ip_address, response_mac_address, node_socket)

    print(f"ARP tables updated. [Completed]")
    node_socket.send(bytes(f"Node connected to router with mac {self.router_mac} and IP address of {self.router_ip_address}.", "utf-8"))
  
  def broadcast_packet(
    self,
    # src_ip,
    packet
  ):
    # for node_ip in self.arp_table_socket.keys:
    #   if node_ip != src_ip:
    #     node_socket = self.arp_table_socket[node_ip]
    #     node_socket.send(bytes(packet, "utf-8"))
    for node_ip in self.arp_table_socket.keys():
      node_socket = self.arp_table_socket[node_ip]
      node_socket.send(bytes(packet, "utf-8"))

  def listen(self, node_socket: socket.socket):
    '''
      Listens to node and broadcasts packet to receipient.
    '''
    while True:
      packet = node_socket.recv(1024).decode("utf-8")
      print("Packet received: ", packet)
      self.broadcast_packet(packet)

  def handle_node(self, node_socket: socket.socket):
    '''
      Started on a seperate thread. 
      1. Establishes identitifying connection with node.
      2. Listens to node indefinitely.
    '''
    while True:
      message = node_socket.recv(1024)
      if message.decode("utf-8") == "connection_request":
        self.connection_request(node_socket)
        break
    
    self.listen(node_socket)


  def run(self):
    print(f"Router starting with mac {self.router_mac} and ip address of {self.router_ip_address}...")
    self.router_socket.listen(self.max_connections)

    try:
      while True:
        node_socket, node_address = self.router_socket.accept()
        threading.Thread(target=self.handle_node, args=(node_socket, )).start() # Start a seperate thread for every client

    except KeyboardInterrupt:
      self.router_socket.close()