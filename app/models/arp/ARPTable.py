from typing import Dict, TypedDict, Union, List
import socket

class ARPTable:
  class ARPRecord(TypedDict):
    '''
      ARPRecord can have no socket connections if it resides in a node. Only sends layer 3 data to router interfaces.
    '''
    mac: str
    corresponding_socket: Union[socket.socket, None] 
  
  arp_table: Dict[str, ARPRecord] = None

  def __init__(self):
    self.arp_table = {}

  def update_arp_table(self, ip_address: str, mac_address: str, corresponding_socket: Union[socket.socket, None] = None) -> None:
    self.arp_table[ip_address] = {
      "mac": mac_address,
      "corresponding_socket": corresponding_socket
    }
    return

  def get_assigned_ip_addresses(self):
    return set(self.arp_table.keys())

  def destroy_arp_connection(self, ip_address: str) -> bool:
    res = self.arp_table.pop(ip_address, False)
    return bool(res)

  def get_corresponding_socket(self, ip_address: str) -> socket.socket:
    arp_record = self.arp_table[ip_address]
    return arp_record["corresponding_socket"]
  
  def get_corresponding_mac(self, ip_address: str) -> str:
    arp_record = self.arp_table[ip_address]
    return arp_record["mac"]
  
  def get_all_sockets(self) -> List[socket.socket]:
    all_arp_records = self.arp_table.values()
    return list(map(lambda arp_record: arp_record["corresponding_socket"] , all_arp_records))

  def to_dict(self) -> dict:
    return self.arp_table