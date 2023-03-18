import os
import socket
import time
import threading
import traceback
from models.payload.EthernetFrame import EthernetFrame
from models.payload.IPPacket import IPPacket
from models.arp.ARPTable import ARPTable
from models.firewall.Firewall import Firewall
from models.protocols.Ping import Ping
from models.protocols.Log import Log
from models.util import print_brk, print_node_help, print_command_not_found

class Node:
  node_ip_address = None # Assigned by router  - See Router.receive_node_connection_data()
  node_mac = None

  router_int_address = None
  router_int_mac = None
  router_int_socket = None

  arp_table = ARPTable()
  # Can initialise firewall with pre-configured lists if needed
  firewall = Firewall()
  ping_protocol = Ping()

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

  def handle_ethernet_frame(self, ethernet_frame: EthernetFrame, corresponding_socket: socket.socket) -> None:
    if ethernet_frame.is_recipient(self.node_mac):
      print("Intended recipient, retrieving data...")

      if ethernet_frame.data.protocol and ethernet_frame.data.protocol[0] == "0":
        self.ping_protocol.handle_ping(ethernet_frame, corresponding_socket)

      if ethernet_frame.data.protocol and ethernet_frame.data.protocol[0] == "1":
        Log.log(ethernet_frame)
        
    else:
      print("Unintended recipient.")

  def listen(self):
    while True:
      try:
        data = self.router_int_socket.recv(1024)
        if not data: # When connection ends from router
          print("Connection from router interface terminated. Node terminated.")
          self.router_int_socket.close()
          os._exit(0)
        
        # Format of paylaod
        # dst_ip|src_ip|dst_mac|src_mac|len_data|<protocol_num>-<str_data>
        payload = data.decode("utf-8")
        payload_sections = payload.split("|")
        is_valid_payload = len(payload_sections) > 1

        # Format of frame data = dst_mac|src_mac|len_data|<protocol_num>-<str_data>
        frame_data = "|".join(payload_sections[2:]) if payload[:2] == "0x" else payload
        src_ip = payload_sections[1] if payload[:2] == "0x" else ""

        # Handle and reply to ARP broadcast query here
        if payload[:10] == "Who has IP":
          print(payload)

        # Check for IP header and drop if in firewall
        elif src_ip in self.firewall.get_blacklist() and not self.firewall.is_disabled():
          print(f"Packet from {src_ip} filtered and dropped by firewall.")

        elif is_valid_payload and frame_data[:2] != "0x":
          # Validation checks for ethernet frame data
          print("Ethernet frame received: ", frame_data)
          ethernet_frame = EthernetFrame.loads(frame_data)
          self.handle_ethernet_frame(ethernet_frame, self.router_int_socket)
          
        print_brk()

      except: # Remove this exception to see potential crashes here
        traceback.print_exc()
        print("Node terminated.")
        return # Should only occur when handle_input receives "quit"

  def send_ip_packet(self, ip_packet: IPPacket, corresponding_socket: socket.socket) -> None:
    print_brk()
    if ip_packet.protocol == "0":
      self.ping_protocol.ping(ip_packet, corresponding_socket)

    else:
      self.router_int_socket.send(bytes(ip_packet.dumps(), "utf-8")) # Temporarily handle outgoing packets for other protocols
      print("IP packet sent. [Completed]")
      print_brk()


  def handle_input(self):
    while True:
      node_input = input()
      if node_input == "quit" or node_input == "q":
        print("Terminating node and connection with router interface...")
        self.router_int_socket.close()
        os._exit(0)

      elif node_input == "help" or node_input == "h":
        print_node_help()

      elif node_input == "eth":
        payload = EthernetFrame.input_sequence(self.node_mac).dumps()
        self.router_int_socket.send(bytes(payload, "utf-8"))
        print("Ethernet frame sent. [Completed]")
        print_brk()

      elif node_input == "ip":
        ip_packet = IPPacket.input_sequence(self.node_ip_address)
        self.send_ip_packet(ip_packet, self.router_int_socket)
      
      elif node_input == "reply":
        print_brk()
        arp_response_payload = EthernetFrame.arp_reply_sequence(self.router_int_mac, self.node_mac).dumps()
        self.router_int_socket.send(bytes(arp_response_payload, "utf-8"))
        print("ARP response sent.")
        print_brk()

      # Handling input to update and view black or whitelists
      elif node_input == "firewall":
        self.firewall.handle_firewall_input()

      elif node_input == "whoami":
        print_brk()
        print(f"Node's IP address is {self.node_ip_address}")
        print(f"Node's MAC address is {self.node_mac}")
        print_brk()

      else:
        print_command_not_found(device = "node")

  def run(self) -> None: 
    print_brk()
    print(f"Node connecting to router interface with mac {self.node_mac}...")
    self.router_int_socket.connect(self.router_int_address)
    self.node_connection_request()
    try:
      threading.Thread(target = self.listen).start()
      print_node_help(False)
      self.handle_input()

    except KeyboardInterrupt:
      self.router_int_socket.close()
