import os
import socket
import time
import threading
import traceback
import json
from typing import List
from models.payload.EthernetFrame import EthernetFrame
from models.payload.IPPacket import IPPacket
from models.arp.ARPTable import ARPTable
from models.dns.DNSTable import DNSTable
from models.dns.DNSRecord import DNSRecord
from models.firewall.Firewall import Firewall
from models.sniffing.Sniffer import Sniffer
from models.protocols.Ping import Ping
from models.protocols.Log import Log
from models.protocols.Kill import Kill
from models.constants import PROTOCOL
from models.util import print_brk, print_node_help, print_command_not_found, print_error, input_ip_sequence, is_valid_domain_name
from config import HOST

class Node:
  device_name = None
  node_ip_address = None # Assigned by router  - See NetworkInterface.receive_node_connection_data()
  node_mac = None

  network_int_address = None
  network_int_mac = None
  network_int_socket = None

  arp_table = ARPTable()
  dns_table = None
  dns_server_prefix = None
  firewall = Firewall() # Can initialise firewall with pre-configured lists if needed
  ping_protocol = Ping()
  kill_protocol = Kill()
  sniffer = Sniffer()
  malicious_dns_table = None # Initialize in the config

  def __init__(
    self,
    device_name: str,
    node_mac: str,
    network_int_mac: str,
    network_int_port: int,
    network_int_host: str = HOST,
    dns_server_prefix: str = None,
    dns_records: List = None,
    malicious_dns_records: List = None
  ):
    self.device_name = device_name
    self.node_mac = node_mac
    self.network_int_address = (network_int_host, network_int_port)
    self.network_int_mac = network_int_mac
    self.network_int_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.dns_table = DNSTable(dns_records)
    self.dns_server_prefix = dns_server_prefix
    self.malicious_dns_table = DNSTable(malicious_dns_records)

  def receive_node_connection_data(self):
    print("Awaiting node connection data... [1/3]")
    assigned_ip_address = None
    network_int_mac = None

    while True:
      data = self.network_int_socket.recv(1024).decode('utf-8')
      if data == "provide_node_connection_data_completed":
        break
      
      data = data.split("|")
      if (len(data) > 1): 
        assigned_ip_address, network_int_mac = data
    
    print(f"IP address {assigned_ip_address} assigned.")
    print(f"Updating ARP tables... [2/3]")
    self.arp_table.update_arp_table(assigned_ip_address, network_int_mac, self.network_int_socket)
    self.node_ip_address = assigned_ip_address
    return self.node_ip_address, network_int_mac

  def response_mac_address(self):
    print("Sending MAC... [3/3]")
    self.network_int_socket.send(bytes(f"{self.node_mac}" ,"utf-8"))
    time.sleep(1)
    self.network_int_socket.send(bytes(f"request_mac_address_completed" ,"utf-8"))
    print(f"{self.device_name} MAC {self.node_mac} sent.")
    return True

  def node_connection_request(self):
    self.network_int_socket.send(bytes("node_connection_request", "utf-8"))
    ip_assigned = False
    mac_provided = False

    while not ip_assigned or not mac_provided:
      message = self.network_int_socket.recv(1024).decode('utf-8')
      if (message == "provide_node_connection_data"):
        ip_assigned, _ = self.receive_node_connection_data()

      elif (message == "request_mac_address"):
        mac_provided = self.response_mac_address()

    print(f"Connection established with router's network interface with MAC of {self.network_int_mac}.")
    print(f"{self.device_name} connection request completed. [Completed]")
    print_brk()
    return

  def handle_ethernet_frame(self, ethernet_frame: EthernetFrame, corresponding_socket: socket.socket) -> None:
    if ethernet_frame.is_recipient(self.node_mac):
      print("Intended recipient, retrieving data...")

      if ethernet_frame.data.protocol and ethernet_frame.data.protocol[0] == PROTOCOL["PING"]:
        self.ping_protocol.handle_ping(ethernet_frame, corresponding_socket)

      elif ethernet_frame.data.protocol and ethernet_frame.data.protocol[0] == PROTOCOL["LOG"]:
        Log.log(ethernet_frame)

      elif ethernet_frame.data.protocol and ethernet_frame.data.protocol[0] == PROTOCOL["KILL"]:
        self.kill_protocol.kill(self.arp_table)

      elif ethernet_frame.data.protocol and ethernet_frame.data.protocol[0] == PROTOCOL["DNS_QUERY"]:
        self.handle_dns_response(ethernet_frame)

      elif ethernet_frame.data.protocol and ethernet_frame.data.protocol[0] == PROTOCOL["ETH"]:
        print(f"Ethernet frame data: {ethernet_frame.data.data}")

    elif self.sniffer.is_sniffing:
      print("Sniffing enabled...")
      sniffed_data = ethernet_frame.data.data
      if self.sniffer.is_dns_spoofing:
        try:
          # format: {"domain_name":..., "ip_address":...}
          # exception thrown here if is not DNS query
          sniffed_data = json.loads(ethernet_frame.data.data) # type dict

          # Capture and check if it is domain name to attack
          domain_name = sniffed_data["domain_name"]

          # Resolve ip in malicious table and assign to malicious ip
          malicious_payload = self.malicious_dns_table.resolve(domain_name)
          if (
              malicious_payload is None or 
              ethernet_frame.data.dest_ip == self.node_ip_address or
              ethernet_frame.data.src_ip == self.node_ip_address
            ):
            pass
          else:
            malicious_ip_address = malicious_payload["ip_address"]
            print(f"DNS response prepared with DNS record of {malicious_payload}.")
            ip_packet = IPPacket(ethernet_frame.data.dest_ip, malicious_ip_address, PROTOCOL["DNS_QUERY"], json.dumps(malicious_payload))
            self.send_ip_packet(ip_packet, corresponding_socket, has_bottom_break=False)

        except json.decoder.JSONDecodeError:
          pass

      print(f"Ethernet frame data: {sniffed_data}")

    else:
      print("Unintended recipient.")

  def listen(self):
    while True:
      try:
        data = self.network_int_socket.recv(1024)
        if not data: # When connection ends from network interface
          print(f"Connection from router's network interface terminated. {self.device_name} terminated.")
          self.network_int_socket.close()
          os._exit(0)
        
        '''
          Valid payload will always be an ethernet packet.
            1. Check validity of payload by checking that incoming message from socket has segments.
            2. If payload valid, load payload data as an EthernetFrame.
            3. EthernetFrame contains IP packet header data within EthernetFrame.data for firewall/protocols.
        '''

        payload = data.decode("utf-8")
        payload_segments = payload.split("|")
        is_valid_payload = len(payload_segments) > 1

        # Handle and reply to ARP broadcast query here
        if payload[:10] == "Who has IP":
          print(payload)

        if is_valid_payload: # Validation checks for ethernet frame data
          # payload = clean_ethernet_payload(payload)
          print(f"Ethernet frame received: {payload}")
          ethernet_frame = EthernetFrame.loads(payload)
          src_ip = ethernet_frame.data.src_ip

          if not self.firewall.is_disabled() and not self.firewall.is_allowed(src_ip):
            print(f"Packet from {src_ip} filtered and dropped by firewall.")
          
          else:
            self.handle_ethernet_frame(ethernet_frame, self.network_int_socket)
          
        print_brk()

      except: # Remove this exception to see potential crashes here
        traceback.print_exc()
        print(f"{self.device_name} terminated.")
        return # Should only occur when handle_input receives "quit"

  def send_dns_query(self, address: str) -> str:
    print("Sending DNS query...")
    ip_packet = IPPacket(self.dns_server_prefix + "F", self.node_ip_address, PROTOCOL["DNS_QUERY"], address)
    self.send_ip_packet(ip_packet, self.network_int_socket)
    print(f"DNS query sent to DNS server at prefix {self.dns_server_prefix}.")

  
  def handle_dns_response(self, ethernet_frame: EthernetFrame) -> str:
    dns_query_response = ethernet_frame.data.data
    print(f"DNS query response received of {dns_query_response}.")
    dns_record_data = json.loads(dns_query_response.replace("'",'"'))
    print("Updating local DNS cache...")
    self.dns_table.update_resolution_table(DNSRecord(domain_name=dns_record_data["domain_name"], ip_address=dns_record_data["ip_address"]))
    print("Local DNS cache updated.")

  def get_input_address(self) -> str:
    '''
      Processes input address from user, resolving domain name locally if possible. Else, resolve domain name based on dns_server_prefix.
    '''
    dest_address = input("Enter destination address...\n> ")
    while True:
      if dest_address[:2] == "0x":
        return dest_address
      
      if not is_valid_domain_name(dest_address):
        dest_address = input("Destination address invalid. Please enter destination address again...\n> ")
        continue # Continue prompting user
      
      if not self.dns_table.resolve(dest_address):
        self.send_dns_query(dest_address)
      elif self.dns_table.resolve(dest_address)["ip_address"] is None:
        self.dns_table.remove_record(dest_address) # If previous resolution is None, remove record and try again
        self.send_dns_query(dest_address)
      
      dns_query_time_out = 5
      current_time = 2
      while not (self.dns_table.resolve(dest_address)) and not (current_time == dns_query_time_out):
        print(f"Awaiting DNS response{'.' * (current_time % 3 + 1)}")
        current_time += 1
        time.sleep(1)

      dns_record = self.dns_table.resolve(dest_address)
      if dns_record and dns_record["ip_address"]:
        dest_ip_address = dns_record["ip_address"]
        print(f"Destination address of {dest_address} successfully resolved to IP address of {dest_ip_address}.")
        return dest_ip_address

      print("DNS failed to resolve, please try again later.")
      return

  def send_ip_packet(self, ip_packet: IPPacket, corresponding_socket: socket.socket, has_top_break: bool = True, has_bottom_break: bool = True) -> None:
    if has_top_break:print_brk()

    if ip_packet.protocol == PROTOCOL["PING"]:
      self.ping_protocol.ping(ip_packet, corresponding_socket)

    else:
      self.network_int_socket.send(bytes(ip_packet.dumps(), "utf-8")) # Temporarily handle outgoing packets for other protocols
      print("IP packet sent. [Completed]")
      if has_bottom_break: print_brk()


  def handle_input(self):
    while True:
      node_input = input()
      if node_input == "quit" or node_input == "q":
        print("Terminating node and connection with router interface...")
        self.network_int_socket.close()
        os._exit(0)

      elif node_input == "help" or node_input == "h":
        print_node_help()

      elif node_input == "eth":
        payload = EthernetFrame.input_sequence(self.node_mac).dumps()
        self.network_int_socket.send(bytes(payload, "utf-8"))
        print("Ethernet frame sent. [Completed]")
        print_brk()

      elif node_input == "ip":
        print("Create a IP packet by entering the following infomration into the console.")
        dest_ip = self.get_input_address()
        if not dest_ip:
          print_error(has_top_break=False)
          continue

        ip_packet = IPPacket.input_sequence(self.node_ip_address, dest_ip)
        if ip_packet:
          self.send_ip_packet(ip_packet, self.network_int_socket)
        else:
          print_error()

      elif node_input == "arp":
        print("Displaying all ARP tables...")
        self.arp_table.pprint()
        print_brk()

      elif node_input == "dns":
        print("Displaying all local DNS records...")
        self.dns_table.pprint()
        if bool(self.malicious_dns_table.resolution_table):
          print("Displaying malicious DNS records...")
          self.malicious_dns_table.pprint()
        print_brk()

      elif node_input == "reply":
        print_brk()
        arp_response_payload = EthernetFrame.arp_reply_sequence(self.network_int_mac, self.node_mac).dumps()
        self.network_int_socket.send(bytes(arp_response_payload, "utf-8"))
        print("ARP response sent.")
        print_brk()

      # Handling input to update and view black or whitelists
      elif node_input == "firewall":
        self.firewall.handle_firewall_input()

      elif node_input == "kill":
        self.kill_protocol.handle_kill_protocol_input()

      elif node_input == "sniff":
        self.sniffer.handle_sniffer_input()

      elif node_input == "spoof":
        spoof_ip = input_ip_sequence("Enter the IP address you want to spoof.\n> ")
        print_brk()

        dest_ip = self.get_input_address()
        if not dest_ip:
          print_error(has_top_break=False)
          continue

        ip_packet = IPPacket.input_sequence(spoof_ip, dest_ip)
        if ip_packet:
          self.send_ip_packet(ip_packet, self.network_int_socket)
        else:
          print_command_not_found(device = "node")

      elif node_input == "whoami":
        print_brk()
        print(f"{self.device_name}'s IP address is {self.node_ip_address}")
        print(f"{self.device_name}'s MAC address is {self.node_mac}")
        print_brk()

      else:
        print_command_not_found(device = "node")

  def run(self) -> None: 
    print_brk()
    print(f"{self.device_name} connecting to router's network interface with mac {self.node_mac}...")
    self.network_int_socket.connect(self.network_int_address)
    self.node_connection_request()
    try:
      threading.Thread(target = self.listen).start()
      print_node_help(False)
      self.handle_input()

    except KeyboardInterrupt:
      self.network_int_socket.close()
