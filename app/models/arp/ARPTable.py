from typing import Dict, TypedDict, Union, List
import socket
import json
from .ARPRecord import ARPRecord

class ARPTable:
  arp_table: Dict[str, ARPRecord] = None

  def __init__(self):
    self.arp_table = {}

  def update_arp_table(self, ip_address: str, mac_address: str, corresponding_socket: Union[socket.socket, None] = None) -> None:
    self.arp_table[ip_address] = {
      "mac": mac_address,
      "corresponding_socket": corresponding_socket
    }
    return

  def get_used_ip_addresses(self):
    return set(self.arp_table.keys())

  def destroy_arp_connection(self, ip_address: str, mac_address: str) -> bool:
    '''
      Destroys an ARP connection only if IP address and MAC address are aligned.
      I.e. if another node has assumed IP address, connection won't be destroyed.
    '''
    res = False
    arp_record = self.arp_table.get(ip_address, None)
    if arp_record and (arp_record["mac"] == mac_address):
      res = self.arp_table.pop(ip_address, False)
    return bool(res)

  def get_corresponding_socket(self, ip_address: str) -> socket.socket:
    arp_record = self.arp_table[ip_address]
    return arp_record["corresponding_socket"]

  def get_corresponding_socket_from_prefix(self, ip_prefix:str) -> socket.socket:
    target_address = None
    for ip_address in self.arp_table.keys():
      if ip_prefix in ip_address:
        target_address = ip_address
        break
    
    if target_address:
      return self.arp_table[target_address]["corresponding_socket"]
    return None
  
  def get_corresponding_mac(self, ip_address: str) -> Union[str, None]:
    arp_record = self.arp_table.get(ip_address, None)
    if arp_record:
      return arp_record["mac"]
    return None

  def get_all_ip_addresses(self) -> List[str]:
    return list(self.arp_table.keys())

  def get_all_arp_records(self) -> List[ARPRecord]:
    return self.arp_table.values()
  
  def get_all_sockets(self) -> List[socket.socket]:
    return list(map(lambda arp_record: arp_record["corresponding_socket"] , self.get_all_arp_records()))

  def to_dict(self) -> dict:
    return self.arp_table

  def pprint(self) -> None:
    print(json.dumps({ip_address: self.arp_table[ip_address]["mac"] for ip_address in self.arp_table}, indent=2))