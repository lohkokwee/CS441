import socket
import time
import threading
from models.util import make_packet

class Node:
  node_ip_address = None # Assigned by router - See Router.assign_ip_address()
  node_mac = None

  router_address = None
  router_mac = None
  router_socket = None

  def __init__(
    self,
    node_mac: str,
    router_mac: str,
    router_port: int,
    router_host: str = "localhost"
  ):
    self.node_mac = node_mac

    self.router_address = (router_host, router_port)
    self.router_mac = router_mac

    self.router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def assign_ip_address(self):
    print("Awaiting IP address...")
    while True:
      message = self.router_socket.recv(1024).decode('utf-8')
      if message == "assign_ip_address_completed":
        break
      self.node_ip_address = message
    print(f"IP address {self.node_ip_address} assigned.")
    return self.node_ip_address

  def response_mac_address(self):
    print("Sending MAC...")
    self.router_socket.send(bytes(f"{self.node_mac}" ,"utf-8"))
    time.sleep(2)
    self.router_socket.send(bytes(f"request_mac_address_completed" ,"utf-8"))
    print(f"Node MAC {self.node_mac} sent.")
    return True

  def connection_request(self):
    self.router_socket.send(bytes("connection_request", "utf-8"))
    ip_assigned = False
    mac_provided = False

    while not ip_assigned or not mac_provided:
      message = self.router_socket.recv(1024).decode('utf-8')
      if (message == "assign_ip_address"):
        ip_assigned = self.assign_ip_address()

      elif (message == "request_mac_address"):
        mac_provided = self.response_mac_address()
    return

  def listen(self):
    while True:
      packet = self.router_socket.recv(1024).decode("utf-8")
      print(packet)

  def handle_input(self):
    while True:
      node_input = input()
      if node_input == "quit":
        exit(1)
      elif node_input:
        print("Payload:", node_input)
        dest_ip = input("Enter destination IP address: ")
        packet = make_packet(dest_ip, self.node_ip_address, node_input)
        self.router_socket.send(bytes(packet, "utf-8"))

  def run(self) -> None: 
    print(f"Node connecting to router with mac {self.node_mac}...")
    self.router_socket.connect(self.router_address)
    self.connection_request()
    try:
      threading.Thread(target=self.listen).start()
      self.handle_input()

    except KeyboardInterrupt:
      self.router_socket.close()
