import os
import socket
import threading
import json
from typing import List
from models.node.Node import Node
from models.payload.EthernetFrame import EthernetFrame
from models.payload.IPPacket import IPPacket
from models.dns.DNSTable import DNSTable
from models.dns.DNSRecord import DNSRecord
from models.constants import PROTOCOL
from models.util import print_brk, print_dns_help, print_command_not_found, input_ip_sequence

class DNS(Node):
  '''
    A DNS server implementation of a Node.
  '''
  def __init__(
    self,
    node_mac: str,
    router_int_mac: str,
    router_int_port: int,
    router_int_host: str = "localhost",
    dns_records: List = None
  ):
    super().__init__(node_mac, router_int_mac, router_int_port, router_int_host, dns_records=dns_records)

  def dns_response(self, ethernet_frame: EthernetFrame, corresponding_socket: socket.socket):
    print("Preparing DNS response...")
    payload = self.dns_table.resolve(ethernet_frame.data.data)
    if (payload is None):
      payload = DNSRecord(domain_name=ethernet_frame.data.data, ip_address=None)
    print(f"DNS response prepared with DNS record of {payload}.")
    ip_packet = IPPacket(ethernet_frame.data.src_ip, self.node_ip_address, PROTOCOL["DNS_QUERY"], json.dumps(payload))
    self.send_ip_packet(ip_packet, corresponding_socket, has_bottom_break=False)
    pass

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
        print("DNS query received.")
        self.dns_response(ethernet_frame, corresponding_socket)

    else:
      print("Unintended recipient.")

  def handle_input(self):
    while True:
      node_input = input()
      if node_input == "quit" or node_input == "q":
        print("Terminating DNS server node and connection with router interface...")
        self.router_int_socket.close()
        os._exit(0)

      elif node_input == "help" or node_input == "h":
        print_dns_help()

      elif node_input == "arp":
        print("Displaying all ARP tables...")
        self.arp_table.pprint()
        print_brk()

      elif node_input == "dns":
        print("Displaying all DNS records...")
        self.dns_table.pprint()
        print_brk()
    
      elif node_input == "whoami":
        print_brk()
        print(f"DNS server node's IP address is {self.node_ip_address}")
        print(f"DNS server node's MAC address is {self.node_mac}")
        print_brk()

      else:
        print_command_not_found(device = "dns")

  def run(self) -> None: 
    print_brk()
    print(f"DNS server node connecting to router interface with mac {self.node_mac}...")
    self.router_int_socket.connect(self.router_int_address)
    self.node_connection_request()
    try:
      threading.Thread(target = self.listen).start()
      print_dns_help(False)
      self.handle_input()

    except KeyboardInterrupt:
      self.router_int_socket.close()