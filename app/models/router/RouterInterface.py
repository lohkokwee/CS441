import os
import socket
import time
import threading
from models.util import print_brk
from models.arp.ARPTable import ARPTable
from models.util import print_brk, print_router_help, print_command_not_found

class RouterInterface:
  router_int_address = None
  router_int_ip_address = None
  router_int_mac = None
  router_int_socket = None

  router_int_relay_addresses: list[tuple] = []

  max_connections = 0
  arp_table = ARPTable()
  router_int_arp_table = ARPTable()

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
    assigned_ip_addresses = self.arp_table.get_assigned_ip_addresses()
    for i in range(self.max_connections):
      check_ip = f"0x{(int(self.router_int_ip_address, 0) + 9 + i):X}"
      if not (check_ip in assigned_ip_addresses):
        return check_ip
    return False

  def provide_node_connection_data(self, corresponding_socket: socket.socket) -> tuple[str, str]:
    assigned_ip_address = self.get_available_ip_address()
    data = f"{assigned_ip_address}|{self.router_int_mac}"
    corresponding_socket.send(bytes("provide_node_connection_data" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"{data}" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes("provide_node_connection_data_completed" ,"utf-8"))
    time.sleep(1)
    return assigned_ip_address, self.router_int_mac

  def request_mac_address(self, corresponding_socket: socket.socket) -> str:
    corresponding_socket.send(bytes("request_mac_address" ,"utf-8"))
    while True:
      message = corresponding_socket.recv(1024).decode("utf-8")
      if (message == "request_mac_address_completed"):
        break
      response_mac_address = message
    
    return response_mac_address

  def destroy_arp_connections(self, ip_address: str) -> None:
    is_destroyed = self.arp_table.destroy_arp_connection(ip_address)
    if not is_destroyed:
      self.router_int_arp_table.destroy_arp_connection(ip_address)
    return

  def node_connection_response(self, corresponding_socket: socket.socket) -> tuple[str, str]:
    '''
      Establishes arp tables for socket and mac.
      1. Provide connection data (assign free IP address and provide router interface MAC address).
      2. Request Node's MAC address.
      Returns assigned IP address and MAC of device.
    '''
    print(f"Node connection request received.")
    print(f"Assigning free IP address... [1/3]")
    assigned_ip_address, _ = self.provide_node_connection_data(corresponding_socket)

    print(f"Requesting MAC address... [2/3]")
    response_mac_address = self.request_mac_address(corresponding_socket)

    print(f"Updating ARP tables... [3/3]")
    self.arp_table.update_arp_table(assigned_ip_address, response_mac_address, corresponding_socket)

    print(f"Connection established. [Completed]")
    print_brk()
    # corresponding_socket.send(bytes(f"Connection established with router interface with MAC of {self.router_int_mac} and IP address of {self.router_int_ip_address}.", "utf-8"))
    return assigned_ip_address, response_mac_address

  def broadcast_ethernet_frame_data(self, payload: str):
    '''
      Emulates effect of ethernet broadcast of payload through socket unicast.
    '''
    print("Broadcasting ethernet frame to connected MACs...")
    connected_sockets = self.arp_table.get_all_sockets()
    for connected_socket in connected_sockets:
      connected_socket.send(bytes(payload, "utf-8"))
    print("Ethernet frame broadcasted.")

  def listen(self, corresponding_socket: socket.socket, ip_address: str, mac_address: str):
    '''
      Listens to node and broadcasts packet to receipient.
    '''
    while True:
      try:
        data = corresponding_socket.recv(1024)
        if not data:
          print(f"Connection terminated from IP address of {ip_address} and MAC of {mac_address}.")
          print(f"Closing corresponding connections... [1/2]")
          corresponding_socket.close()
          print(f"Unassigning IP address from ARP tables... [2/2]")
          self.destroy_arp_connections(ip_address)
          print(f"Connection to {mac_address} terminated. [Completed]")
          print_brk()
          return # End thread

        payload = data.decode("utf-8")
        is_valid_payload = len(payload.split("|")) > 1
        if is_valid_payload and payload[:2] != "0x":
          print("Ethernet frame received: ", payload)
          self.broadcast_ethernet_frame_data(payload)
        print_brk()
      except ConnectionResetError as cre:
        # Raise exception here when node connection closes
        # For windows OS
        print(f"Connection terminated from IP address of {ip_address} and MAC of {mac_address}.")
        print(f"Closing corresponding connections... [1/2]")
        corresponding_socket.close()
        print(f"Unassigning IP address from ARP tables... [2/2]")
        self.destroy_arp_connections(ip_address)
        print(f"Connection to {mac_address} terminated. [Completed]")
        print_brk()
        return # End thread

      except:
        corresponding_socket.close()
        os._exit(0)

  def provide_router_int_connection_data(self, corresponding_socket: socket.socket):
    data = f"{self.router_int_ip_address}|{self.router_int_mac}"
    corresponding_socket.send(bytes(f"provide_router_int_connection_data" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"{data}" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"provide_router_int_connection_data_completed" ,"utf-8"))
    time.sleep(1)
    return

  def receive_router_int_connection_data(self, corresponding_socket: socket.socket) -> list[str]:
    ip_received = None
    mac_received = None

    while True:
      data = corresponding_socket.recv(1024).decode('utf-8')
      if data == f"provide_router_int_connection_data_completed":
        break
      
      data = data.split("|")
      if (len(data) > 1): 
        ip_received, mac_received = data

    print(f"Connection router's IP address of {ip_received} and MAC of {mac_received} received.")
    return ip_received, mac_received
  
  def router_int_connection_request(self, corresponding_socket: socket.socket) -> tuple[str, str]:
    '''
      Establishes arp tables for socket and mac for router interface that is connecting to another router.
      1. Request for target router's IP address.
      2. Request for target router's IP address MAC address.
    '''
    corresponding_socket.send(bytes("router_int_connection_request", "utf-8"))
    corresponding_ip_address = None
    corresponding_mac_address = None
    data_provided = False
    print("Connecting to router interface...")

    while (corresponding_ip_address is None) or (corresponding_mac_address is None) or not data_provided:
      data = corresponding_socket.recv(1024)
      if not data:
        print_brk()
        print("Connection from router interface terminated prematurely.") # Router interface connection ends before ARP established
        print(f"Closing corresponding connections... [1/2]")
        corresponding_socket.close()
        print(f"Unassigning IP address from ARP tables... [2/2]")
        if corresponding_ip_address:
          self.destroy_arp_connections(corresponding_ip_address)
        print(f"Connection terminated. [Completed]")
        print_brk()
        return corresponding_ip_address, corresponding_mac_address # End thread

      message = data.decode('utf-8')
      if (message == "provide_router_int_connection_data"):
        print(f"Receiving connection router's IP address and MAC... [1/3]")
        corresponding_ip_address, corresponding_mac_address = self.receive_router_int_connection_data(corresponding_socket)

      elif (message == "request_router_int_connecting_data"):
        print(f"Providing connecting data... [2/3]")
        data_provided = self.provide_router_int_connecting_data(corresponding_socket)
    
    print(f"Updating ARP tables... [3/3]")
    self.router_int_arp_table.update_arp_table(corresponding_ip_address, corresponding_mac_address, corresponding_socket)
    print(f"Connected to router interface. [Completed]")
    print_brk()
    return corresponding_ip_address, corresponding_mac_address
  
  def request_router_int_connecting_data(self, corresponding_socket: socket.socket) -> list[str]:
    corresponding_socket.send(bytes(f"request_router_int_connecting_data" ,"utf-8"))
    while True:
      message = corresponding_socket.recv(1024).decode('utf-8')
      if message == f"provide_router_int_connecting_data_completed":
        break
      data = message.split("|")
    print(f"Connecting router's IP address of {data[0]} and MAC of {data[1]} received.")
    return data
  
  def provide_router_int_connecting_data(self, corresponding_socket: socket.socket):
    data = f"{self.router_int_ip_address}|{self.router_int_mac}"
    corresponding_socket.send(bytes(f"{data}" ,"utf-8"))
    time.sleep(1)
    corresponding_socket.send(bytes(f"provide_router_int_connecting_data_completed" ,"utf-8"))
    time.sleep(1)
    print(f"Connecting data provided.")
    return True

  def router_int_connection_response(self, corresponding_socket: socket.socket) -> tuple[str, str]:
    '''
      Establishes arp tables for socket and mac for router interface that is trying to connect to this router.
      1. Provide own IP address.
      2. Request MAC address.
    '''
    print(f"Router interface connection request received.")
    print(f"Providing own IP address and MAC... [1/3]")
    self.provide_router_int_connection_data(corresponding_socket)

    print(f"Requesting connecting router's IP address and MAC... [2/3]")
    connecting_ip_address, connecting_mac = self.request_router_int_connecting_data(corresponding_socket)

    print(f"Updating ARP tables... [3/3]")
    self.router_int_arp_table.update_arp_table(connecting_ip_address, connecting_mac, corresponding_socket)

    print(f"Connection established. [Completed]")
    print_brk()
    return connecting_ip_address, connecting_mac

  def handle_connection(self, corresponding_socket: socket.socket):
    '''
      Started on a seperate thread. 
      1. Establishes identitifying connection with node/router interface.
      2. Listens to node indefinitely.
    '''
    ip_address = None

    while True:
      data = corresponding_socket.recv(1024)
      if not data:
        print("Connection from node terminated prematurely.") # Node connection ends before ARP established
        print(f"Closing corresponding connections... [1/2]")
        corresponding_socket.close()
        print(f"Unassigning IP address from ARP tables... [2/2]")
        if ip_address:
          self.destroy_arp_connections(corresponding_ip_address)
        print(f"Connection terminated. [Completed]")
        print_brk()
        return # End thread

      message = data.decode("utf-8")
      if message == "node_connection_request":
        ip_address, mac_address = self.node_connection_response(corresponding_socket)
        break
      elif message == "router_int_connection_request":
        ip_address, mac_address = self.router_int_connection_response(corresponding_socket)
        break
    
    self.listen(corresponding_socket, ip_address, mac_address)

  def handle_router_int_connection(self, corresponding_socket: socket.socket):
    '''
      Create connection with other router interfaces.
      1. Initiates connection for a router interface address.
      2. Start a thread listen to the new connection if identifying connection established.
    '''
    ip_address, mac_address = self.router_int_connection_request(corresponding_socket)
    if ip_address and mac_address:
      threading.Thread(target=self.listen, args=(corresponding_socket, ip_address, mac_address, )).start()

  def handle_input(self):
    while True:
      router_input = input()
      if router_input == "quit":
        print("Terminating router and connection with other interfaces...")
        self.router_int_socket.close()
        os._exit(0)

      elif router_input == "whoami":
        print(f"Router's address is {self.router_int_address}")
        print(f"Router's IP address is {self.router_int_ip_address}")
        print(f"Router's MAC address is {self.router_int_mac}")
        print(f"Router's relay addresses are {self.router_int_relay_addresses}")

      elif router_input == "arp":
        print("IP Address \t MAC Address")
        print_brk()
        for ip_add, details in self.arp_table.to_dict().items():
          print(f"{ip_add} \t\t {details['mac']}")

      # todo: implement ARP broadcast

      elif router_input == "help":
        print_router_help()
      
      else:
        print_command_not_found(device = "router_interface")

  def run(self):
    print_brk()
    print(f"Router interface starting with mac {self.router_int_mac} and ip address of {self.router_int_ip_address}...")
    print_brk()
    if (len(self.router_int_relay_addresses) != 0):
      print("Connecting to configured router interfaces...")
      print_brk()
      for address in self.router_int_relay_addresses:
        corresponding_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        corresponding_socket.connect(address)
        self.handle_router_int_connection(corresponding_socket)
      
    print_router_help()
    # opens another thread to handle input
    threading.Thread(target=self.handle_input).start()

    try:
      self.router_int_socket.listen(self.max_connections)
      while True:
        corresponding_socket, corresponding_address = self.router_int_socket.accept()
        # Start a seperate thread for every client
        threading.Thread(target=self.handle_connection, args=(corresponding_socket, )).start()

    except:
      print(f"Router interface {self.router_int_ip_address} terminating.")
      corresponding_socket.close()
      print_brk()
      os._exit(0)