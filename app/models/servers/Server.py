import os
import socket
import threading
import traceback
from typing import List
from models.nic.NetworkInterface import NetworkInterface
from models.payload.IPPacket import IPPacket
from models.firewall.Firewall import Firewall
from models.util import print_server_help, print_command_not_found, print_brk
from config import HOST

class Server(NetworkInterface):
  '''
    Servers implementing router interfaces to relay information to different networks.
    Maintains NetworkInterface's functionality.
  '''
  firewall = None

  def __init__(
    self,
    device_name: str,
    network_int_ip_address: str,
    network_int_mac: str,
    network_int_port: int,
    max_connections: int,
    network_int_relay_addresses: list[tuple] = [],
    network_int_host: str = HOST,
    whitelist: List[str] = []
  ):
    super().__init__(
      device_name,
      network_int_ip_address,
      network_int_mac,
      network_int_port,
      max_connections,
      network_int_relay_addresses, network_int_host
    )
    self.firewall = Firewall(whitelist=whitelist, blacklist_disabled=True, whitelist_disabled=False)

  def route_ip_packet_data(self, ip_packet: IPPacket):
    '''
      Emulates IP packet routing to nodes with socket unicast.
      1. Checks if IP packet has the same prefix as current LAN (broadcast within same LAN)
      2. If different, checks if same prefix with LANs within conencted interfaces (valid_ips would have one result)
    '''
    print("Checking IP packet destination... [1/2]")
    ip_prefix = ip_packet.dest_ip_prefix()
    
    if ip_prefix == self.network_int_ip_prefix:
      if (
        not self.firewall.is_disabled() and self.firewall.is_allowed(ip_packet.source)
      ) or (
        self.firewall.is_disabled()
      ):
        print("Broadcasting de-capsulated IP packets to connected nodes... [2/2]")
        dest_mac = None
        is_broadcast_channel = ip_packet.is_broadcast_address()
        if not is_broadcast_channel:
          dest_mac = self.arp_table.get_corresponding_mac(ip_packet.destination)
        ethernet_frame_with_headers: EthernetFrame = ip_packet.to_eth_frame(dest_mac, self.network_int_mac)
        self.broadcast_ethernet_frame_data(ethernet_frame_with_headers, is_broadcast_channel)
      else:
        print("Packet dropped... [2/2]")
      print("IP packet handled. [Completed]")

    else:
      print("Destination not in LAN.")
      print("Routing packet to LAN with destination prefix... [2/2]")
      next_hop_prefix = self.routing_table.get_next_hop_prefix(ip_prefix)
      if next_hop_prefix:
        corresponding_socket = self.network_int_arp_table.get_corresponding_socket_from_prefix(next_hop_prefix)
        corresponding_socket.send(bytes(ip_packet.dumps(), "utf-8"))
        print("IP packet routed. [Completed]")
      else:
        print("Failed to locate next hop...")
        print("Failed to route IP packet. [Fail]")

  def handle_input(self):
    while True:
      protected_server_input = input()
      if protected_server_input == "quit" or protected_server_input == "q":
        print("Terminating network interface and all existing connections...")
        connected_sockets = self.arp_table.get_all_sockets() + self.network_int_arp_table.get_all_sockets()
        for corresponding_socket in connected_sockets:
          corresponding_socket.close()
        print(f"Network interface {self.network_int_ip_address} terminating.")
        os._exit(0)

      elif protected_server_input == "whoami":
        print_brk()
        print(f"{self.device_name} interface's address is {self.network_int_address}")
        print(f"{self.device_name} interface's IP address is {self.network_int_ip_address}")
        print(f"{self.device_name} interface's MAC address is {self.network_int_mac}")
        print(f"{self.device_name} interface's relay addresses are {self.network_int_relay_addresses}")
        print_brk()


      elif protected_server_input == "broadcast":
        print_brk()
        self.broadcast_arp_query()

      elif protected_server_input == "help" or protected_server_input == "h":
        print_server_help()

      elif protected_server_input == "arp":
        print("Displaying all ARP tables...")
        print("> ARP tables for with connected nodes (IP:MAC).")
        self.arp_table.pprint()
        print("> ARP tables for with connected network interfaces (IP:MAC).")
        self.network_int_arp_table.pprint()
        print_brk()
      
      elif protected_server_input == "arp -n":
        print("Displaying ARP tables with connected nodes (IP:MAC)...")
        self.arp_table.pprint()
        print_brk()

      elif protected_server_input == "arp -r":
        print("Displaying ARP tables with connected network interfaces (IP:MAC)...")
        self.network_int_arp_table.pprint()
        print_brk()

      elif protected_server_input == "ip route":
        print("Displaying IP routing tables with connected network interfaces (IP Prefix:Connected Prefixes)...")
        self.routing_table.pprint()
        print_brk()

      elif protected_server_input == "reconnect":
        print(f"Attempting to reconnect to the following network interfaces {self.failed_network_relays}...")
        self.reconnect()
        print_brk()

      elif protected_server_input == "firewall":
        self.firewall.handle_whitelist_firewall_input(device="server")

      else:
        print_command_not_found(device="server")

  def run(self):
    print_brk()
    print(f"{self.device_name} interface starting with mac {self.network_int_mac} and ip address of {self.network_int_ip_address}...")
    print_brk()
    if (len(self.network_int_relay_addresses) != 0):
      print("Connecting to configured network interfaces...")
      print_brk()
      for address in self.network_int_relay_addresses:
        corresponding_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
          corresponding_socket.connect(address)
          self.handle_network_int_connection(corresponding_socket, address)
        except ConnectionRefusedError:
          print(f"Unable to connect to the network interface with address: {address}.")
          self.failed_network_relays.append(address)
      if (len(self.failed_network_relays) != 0):
        print('Enter "reconnect" to attempt to reconnect to failed network interface connections after turning them on.')
        print_brk()
  
    try:
      threading.Thread(target=self.receive_connections).start()
      print_server_help(False)
      self.handle_input()

    except:
      traceback.print_exc()
      print_brk()
      print(f"{self.device_name} interface {self.network_int_ip_address} terminating.")
      print_brk()
      os._exit(0)