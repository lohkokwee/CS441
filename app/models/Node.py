import socket
import time
import threading
from models.util import make_packet, print_brk, break_packet

class Node:
  node_ip_address = None # Assigned by router  - See Router.assign_ip_address()
  node_mac = None

  router_int_address = None
  router_int_mac = None
  router_int_socket = None

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

  def assign_ip_address(self):
    print("Awaiting IP address...")
    while True:
      message = self.router_int_socket.recv(1024).decode('utf-8')
      if message == "assign_ip_address_completed":
        break
      self.node_ip_address = message
    print(f"IP address {self.node_ip_address} assigned.")
    return self.node_ip_address

  def response_mac_address(self):
    print("Sending MAC...")
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
      if (message == "assign_ip_address"):
        ip_assigned = self.assign_ip_address()

      elif (message == "request_mac_address"):
        mac_provided = self.response_mac_address()
    print("Node connection request completed.")
    print_brk()
    return

  def listen(self):
    while True:
      packet = self.router_int_socket.recv(1024).decode("utf-8")
      if len(packet.split("-")) == 1:
        print("Message received:", packet)
      else:
        data = break_packet(packet)
        print("Payload received:", data.get("payload", None))
      print_brk()

  def handle_input(self):
    while True:
      node_input = input()
      if node_input == "quit":
        exit(1)
      elif node_input:
        print("Payload:", node_input)
        dest_ip = input("Enter destination IP address: ")
        packet = make_packet(dest_ip, self.router_int_mac, self.node_ip_address, self.node_mac, node_input)
        print(f"Packet:", packet)
        print_brk()
        self.router_int_socket.send(bytes(packet, "utf-8"))

  def run(self) -> None: 
    print_brk()
    print(f"Node connecting to router interface with mac {self.node_mac}...")
    self.router_int_socket.connect(self.router_int_address)
    self.node_connection_request()
    try:
      threading.Thread(target=self.listen).start()
      self.handle_input()

    except KeyboardInterrupt:
      self.router_int_socket.close()
