import socket
from typing import List
from models.servers.Server import Server
from models.payload.IPPacket import IPPacket
from models.constants import PROTOCOL
from config import HOST 

class VPNServer(Server):
  '''
    Modifies routing functionality in server.
  '''
  vpn_tunnel_prefix: str = None
  vpn_target_address: str = None

  def __init__(
    self,
    device_name: str,
    network_int_ip_address: str,
    network_int_mac: str,
    network_int_port: int,
    max_connections: int,
    vpn_target_address: str,
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
      network_int_relay_addresses
    )
    self.vpn_tunnel_prefix = vpn_target_address[:3]
    self.vpn_target_address = vpn_target_address

  def route_ip_packet_data(self, ip_packet: IPPacket):
    '''
      Emulates IP packet routing to nodes with socket unicast.
      1. Checks if IP packet has the same prefix as current LAN (broadcast within same LAN)
      2. If different, checks if same prefix with LANs within conencted interfaces (valid_ips would have one result)
    '''
    print("Checking IP packet destination... [1/2]")
    if ip_packet.dest_ip_prefix() == self.network_int_ip_prefix:
      print("Encapsulating packet data for VPN transmission... [2/2]")
      ip_packet.vpn_encap_payload(self.network_int_ip_address, self.vpn_target_address)
      corresponding_socket = self.network_int_arp_table.get_corresponding_socket_from_prefix(self.vpn_tunnel_prefix)
      corresponding_socket.send(bytes(ip_packet.dumps(), "utf-8"))
      print("IP packet routed through VPN tunnel. [Completed]")
    
    else:
      if ip_packet.source_ip_prefix() == self.vpn_tunnel_prefix:
        ip_packet.vpn_decap_payload(self.network_int_ip_address)

      print("Destination not in LAN.")
      print("Routing packet to LAN with destination prefix... [2/2]")
      next_hop_prefix = self.routing_table.get_next_hop_prefix(ip_packet.dest_ip_prefix())
      if next_hop_prefix:
        corresponding_socket = self.network_int_arp_table.get_corresponding_socket_from_prefix(next_hop_prefix)
        corresponding_socket.send(bytes(ip_packet.dumps(), "utf-8"))
        print("IP packet routed. [Completed]")
      else:
        print("Failed to locate next hop...")
        print("Failed to route IP packet. [Fail]")

  def handle_ip_packet(self, ip_packet: IPPacket, corresponding_socket: socket.socket) -> None:
    '''
      Handles what a network interface does with an IP packet.
      1. Checks if current network interface is intended recipient (for routing table update)
      2. If not recipient, route to respective address
    '''
    payload = ip_packet.dumps()
    print("IP packet received: ", payload)

    if (
      (ip_packet.destination == self.network_int_ip_address) 
      and (
        ip_packet.protocol == PROTOCOL["ROUTE_ADD"]
        or ip_packet.protocol == PROTOCOL["ROUTE_REMOVE"]
      )):
      print(f"Intended recipient...")

      if ip_packet.protocol == PROTOCOL["ROUTE_ADD"]:
        print("New route received.")
        print(f"Adding new route to routing table... [1/2]")
        update_prefix, cost, exclusion_ips = ip_packet.get_route_add_data()
        self.routing_table.extend_entry(ip_packet.source[:3], update_prefix, int(cost))
        print("Broadcasting path to neighbouring interfaces... [2/2]")
        self.broadcast_route_add(update_prefix, int(cost), exclusion_ips)
        print("Routing table updated. [Success]")
      
      elif ip_packet.protocol == PROTOCOL["ROUTE_REMOVE"]:
        print(f"Removing new route to routing table... [1/2]")
        update_prefix, exclusion_ips = ip_packet.get_route_remove_data()
        self.routing_table.remove_entire_entry(update_prefix)
        print("Broadcasting removal to neighbouring interfaces... [2/2]")
        self.broadcast_route_remove(update_prefix, exclusion_ips)
        print("Routing table updated. [Success]")

    else:
      self.route_ip_packet_data(ip_packet)


