import os
import socket
import time
import threading
from models.util import print_brk, print_node_help, print_command_not_found
from models.arp.ARPTable import ARPTable
from models.payload.EthernetFrame import EthernetFrame

class Node:
  node_ip_address = None # Assigned by router  - See Router.receive_node_connection_data()
  node_mac = None

  router_int_address = None
  router_int_mac = None
  router_int_socket = None

  arp_table = ARPTable()

  def __init__(
    self,
    node_mac: str,
    router_int_mac: str,
    router_int_port: int,
    router_int_host: str = "localhost"
  ):
    self.node_mac = node_mac
    self.router_int_address = (router_int_host, router_int_port)
    self.router_int_mac = router_int_mac
    self.router_int_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def receive_node_connection_data(self):
    print("Awaiting node connection data... [1/3]")
    assigned_ip_address = None
    router_int_mac = None

    while True:
      data = self.router_int_socket.recv(1024).decode('utf-8')
      if data == "provide_node_connection_data_completed":
        break
      
      data = data.split("|")
      if (len(data) > 1): 
        assigned_ip_address, router_int_mac = data
    
    print(f"IP address {assigned_ip_address} assigned.")
    print(f"Updating ARP tables... [2/3]")
    self.arp_table.update_arp_table(assigned_ip_address, router_int_mac)
    self.node_ip_address = assigned_ip_address
    return self.node_ip_address, router_int_mac

  def response_mac_address(self):
    print("Sending MAC... [3/3]")
    self.router_int_socket.send(bytes(f"{self.node_mac}" ,"utf-8"))
    time.sleep(1)
    self.router_int_socket.send(bytes(f"request_mac_address_completed" ,"utf-8"))
    print(f"Node MAC {self.node_mac} sent.")
    return True

  def node_connection_request(self):
    self.router_int_socket.send(bytes("node_connection_request", "utf-8"))
    ip_assigned = False
    mac_provided = False

    while not ip_assigned or not mac_provided:
      message = self.router_int_socket.recv(1024).decode('utf-8')
      if (message == "provide_node_connection_data"):
        ip_assigned, _ = self.receive_node_connection_data()

      elif (message == "request_mac_address"):
        mac_provided = self.response_mac_address()

    print(f"Connection established with router interface with MAC of {self.router_int_mac}.")
    print("Node connection request completed. [Completed]")
    print_brk()
    return

  def listen(self):
    while True:
      # try:
        data = self.router_int_socket.recv(1024)
        if not data:
          # When connection ends from router
          print("Connection from router interface terminated. Node terminated.")
          self.router_int_socket.close()
          os._exit(0)
        
        payload = data.decode("utf-8")
        is_valid_payload = len(payload.split("|")) > 1
        if is_valid_payload and payload[:2] != "0x":
          print("Ethernet frame received: ", payload)
          frame = EthernetFrame.loads(payload)
          if frame.is_recipient(self.node_mac):
            print("Intended recipient, retrieving data...")
            print(f"Data: {frame.data}")
          else:
            print("Unintended recipient.")
        print_brk()
      # except:
      #   print("Node terminated.")
      #   return # Should only occur when handle_input receives "quit"

  def handle_input(self):
    while True:
      node_input = input()
      if node_input == "quit":
        print("Terminating node and connection with router interface...")
        self.router_int_socket.close()
        os._exit(0)

      elif node_input == "eth":
        payload = EthernetFrame.input_sequence(self.node_mac).dumps()
        self.router_int_socket.send(bytes(payload, "utf-8"))
        print("Ethernet frame sent. [Completed]")
        print_brk()

      elif node_input == "ip":
        pass

      elif node_input == "help":
        print_node_help()
      
      else:
        print_command_not_found(device = "node")

  def run(self) -> None: 
    print_brk()
    print(f"Node connecting to router interface with mac {self.node_mac}...")
    self.router_int_socket.connect(self.router_int_address)
    self.node_connection_request()
    try:
      threading.Thread(target=self.listen).start()
      print_node_help()
      self.handle_input()

    except KeyboardInterrupt:
      self.router_int_socket.close()
