import os
import socket
import time
import threading
from models.arp.ARPTable import ARPTable
from models.payload.IPPacket import IPPacket
from models.payload.EthernetFrame import EthernetFrame
from models.util import print_brk, print_command_not_found, print_router_int_help
import traceback

class RouterInterface:
  '''
    Definitions:
      - int: represents "interface"
  '''
  router_int_address = None
  router_int_ip_address = None
  router_int_ip_prefix = None
  router_int_mac = None
  router_int_socket = None

  router_int_relay_addresses: list[tuple] = []

  max_connections = 0
  arp_table = ARPTable()
  router_int_arp_table = ARPTable()

  # to keep track of which IP to assign MAC to
  arp_last_broadcasted_ip = None
  arp_table_ip_last_updated = None
  arp_response = False

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
    self.router_int_ip_prefix = router_int_ip_address[:3]
    self.router_int_mac = router_int_mac
    self.max_connections = max_connections
    self.router_int_relay_addresses = router_int_relay_addresses

    self.router_int_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.router_int_socket.bind(self.router_int_address)

  def get_available_ip_address(self):
    assigned_ip_addresses = self.arp_table.get_used_ip_addresses()
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

  def destroy_arp_connections(self, ip_address: str, mac_address: str) -> None:
    is_destroyed = self.arp_table.destroy_arp_connection(ip_address, mac_address)
    if not is_destroyed:
      self.router_int_arp_table.destroy_arp_connection(ip_address, mac_address)
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

  def route_ip_packet_data(self, payload: str):
    '''
      Emulates IP packet routing to nodes with socket unicast.
    '''
    print("Checking IP packet destination... [1/2]")
    ip_packet: IPPacket = IPPacket.loads(payload)
    if ip_packet.dest_ip_prefix() == self.router_int_ip_prefix:
      print("Broadcasting de-capsulated IP packets to connected nodes... [2/2]")
      dest_mac = self.arp_table.get_corresponding_mac(ip_packet.destination)

      # Route IP header data to node for firewall to drop as well
      ethernet_frame_with_headers: EthernetFrame = ip_packet.to_eth_frame(dest_mac, self.router_int_mac).dumps()
      self.broadcast_ethernet_frame_data(ethernet_frame_with_headers)

    else:
      print("Destination not in LAN.")
      ip_addresses = self.router_int_arp_table.get_used_ip_addresses()
      print("Routing packet to LAN with destination prefix... [2/2]")
      for ip_address in ip_addresses:
        if ip_address[:3] == ip_packet.dest_ip_prefix(): # If IP prefix matches, send data to IP address
          corresponding_socket = self.router_int_arp_table.get_corresponding_socket(ip_address)
          corresponding_socket.send(bytes(payload, "utf-8"))
          break
    
    print("IP packet routed. [Completed]")

  def handle_ethernet_frame(self, ethernet_frame: EthernetFrame, corresponding_socket: socket.socket) -> None:
    # Checks whether frame is query reply, if yes, update ARP table
    if ethernet_frame.destination == self.router_int_mac and ethernet_frame.data == "arp_response":
      self.arp_response = True
      print(f"ARP response received, updating ARP table for {self.arp_last_broadcasted_ip}...")

      # Update arp_table_ip_last_updated and set arp_last_broadcasted_ip to None
      self.arp_table.update_arp_table(
        self.arp_last_broadcasted_ip,
        ethernet_frame.source,
        corresponding_socket
      )
      self.arp_table_ip_last_updated = self.arp_last_broadcasted_ip
      self.arp_last_broadcasted_ip = None
      print("ARP table successfully updated.")
      
    else:
      payload = ethernet_frame.dumps()
      print("Ethernet frame received: ", payload)
      self.broadcast_ethernet_frame_data(payload)

  def handle_ip_packet(self, ip_packet: IPPacket, corresponding_socket: socket.socket) -> None:
    payload = ip_packet.dumps()
    print("IP packet received: ", payload)
    self.route_ip_packet_data(payload)


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
          self.destroy_arp_connections(ip_address, mac_address)
          print(f"Connection to {mac_address} terminated. [Completed]")
          print_brk()
          return # End thread

        payload = data.decode("utf-8")
        payload_segments = payload.split("|")
        is_valid_payload = len(payload_segments) > 1

        if is_valid_payload:
          if payload[:2] != "0x":
            ethernet_frame = EthernetFrame.loads(payload)
            self.handle_ethernet_frame(ethernet_frame, corresponding_socket)
            
          elif payload[:2] == "0x":
            ip_packet = IPPacket.loads(payload)
            self.handle_ip_packet(ip_packet, corresponding_socket)
        
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
        traceback.print_exc()
        print_brk()
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

    try:
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

    except ConnectionResetError:
      print("Connection reset error in handle_connection")
      return
    
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
      router_int_input = input()
      if router_int_input == "quit" or router_int_input == "q":
        print("Terminating router interface and all existing connections...")
        connected_sockets = self.arp_table.get_all_sockets() + self.router_int_arp_table.get_all_sockets()
        for corresponding_socket in connected_sockets:
          corresponding_socket.close()
        print(f"Router interface {self.router_int_ip_address} terminating.")
        os._exit(0)

      elif router_int_input == "whoami":
        print_brk()
        print(f"Router's address is {self.router_int_address}")
        print(f"Router's IP address is {self.router_int_ip_address}")
        print(f"Router's MAC address is {self.router_int_mac}")
        print(f"Router's relay addresses are {self.router_int_relay_addresses}")
        print_brk()


      elif router_int_input == "broadcast":
        print_brk()
        self.broadcast_arp_query()

      elif router_int_input == "help" or router_int_input == "h":
        print_router_int_help()

      elif router_int_input == "arp":
        print("Displaying all ARP tables...")
        print("> ARP tables for with connected nodes (IP:MAC).")
        self.arp_table.pprint()
        print("> ARP tables for with connected router interfaces (IP:MAC).")
        self.router_int_arp_table.pprint()
        print_brk()
      
      elif router_int_input == "arp -n":
        print("Displaying ARP tables with connected nodes (IP:MAC)...")
        self.arp_table.pprint()
        print_brk()

      elif router_int_input == "arp -r":
        print("Displaying ARP tables with connected router interfaces (IP:MAC)...")
        self.router_int_arp_table.pprint()
        print_brk()
      
      else:
        print_command_not_found(device = "router_interface")
  
  def broadcast_arp_query(self):
    '''
      Broadcasts ARP query to look for MAC with the corresponding IP.
      1. Sends out a broadcast to all hosts within LAN.
      2. If reply matches, then update MAC table.
    '''
    self.arp_response = False
    # 0. Get user input on which IP to get
    target_ip = input("What is the IP address of the MAC you wish to get.\n> ")
    self.arp_last_broadcasted_ip = target_ip

    print("Broadcasting ARP query to all in same LAN...")

    connected_sockets = self.arp_table.get_all_sockets()
    
    # Broadcast
    while not self.arp_response: 
      try:
        for connected_socket in connected_sockets:
          connected_socket.send(bytes(f"Who has IP: {target_ip}, I am {self.router_int_mac}", "utf-8"))
        time.sleep(2)

      except OSError:
        print("OS Error in broadcast_arp_query")
        return
      except UnboundLocalError:
        print("UnboundLocalError in broadcast_arp_query")
        return

  def receive_connections(self):
    '''
      Receives connections on a separate thread for the lifecycle of the router interface.
    '''
    self.router_int_socket.listen(self.max_connections)
    while True:
      corresponding_socket, corresponding_address = self.router_int_socket.accept()
      threading.Thread(target=self.handle_connection, args=(corresponding_socket, )).start()
      

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
  
    try:
      threading.Thread(target=self.receive_connections).start()
      print_router_int_help(False)
      self.handle_input()

    except:
      traceback.print_exc()
      print_brk()
      print(f"Router interface {self.router_int_ip_address} terminating.")
      print_brk()
      os._exit(0)