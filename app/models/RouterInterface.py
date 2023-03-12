import socket
import time
import threading
from typing import Literal
from models.util import break_packet, make_packet, print_brk

class RouterInterface:
  router_int_address = None
  router_int_ip_address = None
  router_int_mac = None
  router_int_socket = None

  router_int_relay_addresses: list[tuple] = []

  max_connections = 0
  arp_table_socket = {}
  arp_table_mac = {}

  router_int_arp_table_socket = {}
  router_int_arp_table_mac = {}

  def __init__(
    self,
    router_int_ip_address: str,
    router_int_mac: str,
    router_int_port: int,
    max_connections: int,
    router_int_relay_addresses: list[tuple] = [],
    router_int_host: str = "localhost"
  ):
    self.router_int_address = (router_int_host, router_int_port)
    self.router_int_ip_address = router_int_ip_address
    self.router_int_mac = router_int_mac
    self.max_connections = max_connections
    self.router_int_relay_addresses = router_int_relay_addresses

    self.router_int_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.router_int_socket.bind(self.router_int_address)

  def get_available_ip_address(self):
    for i in range(self.max_connections):
      check_ip = self.router_int_ip_address[:-1] + chr(ord('A') + i)
      if not (check_ip in self.arp_table_mac):
        return check_ip
    return False

  def assign_ip_addess(self, corresponding_socket: socket.socket) -> str:
    assigned_ip_address = self.get_available_ip_address()
    corresponding_socket.send(bytes("assign_ip_address" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"{assigned_ip_address}" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes("assign_ip_address_completed" ,"utf-8"))
    time.sleep(1)
    return assigned_ip_address

  def request_mac_address(self, corresponding_socket: socket.socket) -> str:
    corresponding_socket.send(bytes("request_mac_address" ,"utf-8"))
    while True:
      message = corresponding_socket.recv(1024).decode("utf-8")
      if (message == "request_mac_address_completed"):
        break
      response_mac_address = message
    
    return response_mac_address

  def build_arp_table(self, ip_address:str, mac_address: str, corresponding_socket: socket.socket, is_router_interface: bool = False) -> None:
    if is_router_interface:
      self.router_int_arp_table_mac[ip_address] = mac_address
      self.router_int_arp_table_socket[ip_address] = corresponding_socket
    else:
      self.arp_table_mac[ip_address] = mac_address
      self.arp_table_socket[ip_address] = corresponding_socket
    return 

  def node_connection_response(self, corresponding_socket: socket.socket):
    '''
      Establishes arp tables for socket and mac.
      1. Assign free IP address.
      2. Request MAC address.
    '''
    print(f"Node connection request received.")
    print(f"Updating ARP tables...")
    
    print(f"Assigning free IP address... [1/3]")
    assigned_ip_address = self.assign_ip_addess(corresponding_socket)

    print(f"Requesting MAC address... [2/3]")
    response_mac_address = self.request_mac_address(corresponding_socket)

    print(f"Updating ARP tables... [3/3]")
    self.build_arp_table(assigned_ip_address, response_mac_address, corresponding_socket)

    print(f"ARP tables updated. [Completed]")
    print_brk()
    corresponding_socket.send(bytes(f"Node connected to router interface with mac {self.router_int_mac} and IP address of {self.router_int_ip_address}.", "utf-8"))
  
  def route_packet(
    self,
    packet
  ):
    '''
      Checks packet headers and route to IP if exists within LAN. Else, forward to other routers.
    '''
    routed_socket: socket.socket | None = None
    packet_data = break_packet(packet)
    dest_ip = packet_data.get("dest_ip")
    new_packet_data = {
      "dest_ip": dest_ip,
      "dest_mac": None,
      "src_ip": packet_data.get("src_ip"),
      "src_mac": self.router_int_mac,
      "payload": packet_data.get("payload")
    }
    for node_ip in self.arp_table_socket.keys():
      if node_ip == dest_ip: 
        # If dest_ip can be found in arp table send directly to destination
        routed_socket = self.arp_table_socket[node_ip]
        new_packet_data["dest_mac"] = self.arp_table_mac[node_ip]

    if routed_socket:
      routed_socket.send(bytes(make_packet(**new_packet_data), "utf-8"))
      return

    # Else hop to other connected routers
    for router_int_ip in self.router_int_arp_table_socket.keys():
      routed_socket = self.router_int_arp_table_socket[router_int_ip]
      new_packet_data["dest_mac"] = self.router_int_arp_table_mac[router_int_ip]
      routed_socket.send(bytes(make_packet(**new_packet_data), "utf-8"))
    return

  def listen(self, corresponding_socket: socket.socket):
    '''
      Listens to node and broadcasts packet to receipient.
    '''
    while True:
      packet = corresponding_socket.recv(1024).decode("utf-8")
      print("Packet received: ", packet)
      print_brk()
      if len(packet.split('-')) != 1:
        self.route_packet(packet)
  
  def provide_router_int_connection_data(self, corresponding_socket: socket.socket):
    data = f"{self.router_int_ip_address}-{self.router_int_mac}"
    corresponding_socket.send(bytes(f"provide_router_int_connection_data" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"{data}" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"provide_router_int_connection_data_completed" ,"utf-8"))
    time.sleep(1)
    return

  def receive_router_int_connection_data(self, corresponding_socket: socket.socket) -> list[str]:
    print(f"Receiving connection router's IP address and MAC...")
    while True:
      message = corresponding_socket.recv(1024).decode('utf-8')
      if message == f"provide_router_int_connection_data_completed":
        break
      data = message.split("-")
    print(f"Connection router's IP address and MAC of {data} received.")
    return data
  
  def router_int_connection_request(self, corresponding_socket: socket.socket):
    '''
      Establishes arp tables for socket and mac for router interface that is conntecting to another router.
      1. Request for target router's IP address.
      2. Request for target router's IP address MAC address.
    '''
    corresponding_socket.send(bytes("router_int_connection_request", "utf-8"))
    corresponding_ip_address = False
    corresponding_mac_address = False
    data_provided = False

    while not corresponding_ip_address or not corresponding_mac_address or not data_provided:
      message = corresponding_socket.recv(1024).decode('utf-8')
      if (message == "provide_router_int_connection_data"):
        corresponding_ip_address, corresponding_mac_address = self.receive_router_int_connection_data(corresponding_socket)

      elif (message == "request_router_int_connecting_data"):
        data_provided = self.provide_router_int_connecting_data(corresponding_socket)
      
    self.build_arp_table(corresponding_ip_address, corresponding_mac_address, corresponding_socket, is_router_interface = True)
    print_brk()
    return
  
  def request_router_int_connecting_data(self, corresponding_socket: socket.socket) -> list[str]:
    corresponding_socket.send(bytes(f"request_router_int_connecting_data" ,"utf-8"))
    while True:
      message = corresponding_socket.recv(1024).decode('utf-8')
      if message == f"provide_router_int_connecting_data_completed":
        break
      data = message.split("-")
    print(f"Connecting router's IP address and MAC of {data} received.")
    return data
  
  def provide_router_int_connecting_data(self, corresponding_socket: socket.socket):
    data = f"{self.router_int_ip_address}-{self.router_int_mac}"
    print(f"Providing connecting data of {data}...")
    corresponding_socket.send(bytes(f"{data}" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"provide_router_int_connecting_data_completed" ,"utf-8"))
    time.sleep(1)
    print(f"Connecting data provided.")
    return True

  def router_int_connection_response(self, corresponding_socket: socket.socket):
    '''
      Establishes arp tables for socket and mac for router interface that is trying to connect to this router.
      1. Provide own IP address.
      2. Request MAC address.
    '''
    print(f"Router interface connection request received.")
    print(f"Updating ARP tables...")
    
    print(f"Providing own IP address and MAC... [1/3]")
    self.provide_router_int_connection_data(corresponding_socket)

    print(f"Requesting connecting router's IP address and MAC... [2/3]")
    connecting_ip_address, connecting_mac = self.request_router_int_connecting_data(corresponding_socket)

    print(f"Updating ARP tables... [3/3]")
    self.build_arp_table(connecting_ip_address, connecting_mac, corresponding_socket, is_router_interface = True)

    print(f"ARP tables updated. [Completed]")
    print_brk()

    corresponding_socket.send(bytes(f"Router interface connected to router interface with mac {self.router_int_mac} and IP address of {self.router_int_ip_address}.", "utf-8"))
    pass

  def handle_connection(self, corresponding_socket: socket.socket):
    '''
      Started on a seperate thread. 
      1. Establishes identitifying connection with node.
      2. Listens to node indefinitely.
    '''
    while True:
      message = corresponding_socket.recv(1024)
      if message.decode("utf-8") == "node_connection_request":
        self.node_connection_response(corresponding_socket)
        break
      elif message.decode("utf-8") == "router_int_connection_request":
        self.router_int_connection_response(corresponding_socket)
        break
    
    self.listen(corresponding_socket)

  def handle_router_int_connection(self, corresponding_socket: socket.socket):
    self.router_int_connection_request(corresponding_socket)
    threading.Thread(target=self.listen, args=(corresponding_socket, )).start()


  def run(self):
    print_brk()
    print(f"Router interface starting with mac {self.router_int_mac} and ip address of {self.router_int_ip_address}...")
    print_brk()
    if (len(self.router_int_relay_addresses) != 0):
      # Create connection with routers
      for address in self.router_int_relay_addresses:
        corresponding_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        corresponding_socket.connect(address)
        self.handle_router_int_connection(corresponding_socket)
    
    self.router_int_socket.listen(self.max_connections)
    try:
      while True:
        corresponding_socket, corresponding_address = self.router_int_socket.accept()
        threading.Thread(target=self.handle_connection, args=(corresponding_socket, )).start() # Start a seperate thread for every client

    except KeyboardInterrupt:
      self.router_int_socket.close()