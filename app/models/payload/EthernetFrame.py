from __future__ import annotations
from models.util import print_brk

class EthernetFrame:
  '''
    Layer 2 communications will not be broadcasted over router interface if no MAC address is found in ARP tables.
  '''

  destination: str = None
  source: str = None
  data_length: int = None
  data: str = None

  def __init__(
    self,
    dest_mac: str,
    src_mac: str,
    data: str
  ):
    self.destination = dest_mac
    self.source = src_mac
    self.data_length = len(data)
    self.data = data
  
  def dumps(self) -> str:
    '''
      Dumps the current EthernetFrame into a str format for transmission.
    '''
    return f"{self.destination}|{self.source}|{self.data_length}|{self.data}"

  @staticmethod
  def loads(data: str) -> EthernetFrame:
    '''
      Receives EthernetFrame in a dumped (str) format from EthernetFrame.dump() and loads an EthernetFrame object.
    '''
    dest_mac, src_mac, data_length, data = data.split("|")
    return EthernetFrame(dest_mac, src_mac, data)

  def is_recipient(self, mac_address: str) -> bool:
    if mac_address == self.destination:
      return True
    return False

  @staticmethod
  def input_sequence(src_mac: str) -> EthernetFrame:
    '''
      Initiates sequence to create EthernetFrame object.
    '''
    print_brk()
    print("Create an ethernet frame by entering the following infomration into the console.")
    dest_mac = input("Enter destination MAC address... [1/2]\n> ")
    print()
    data = input("Enter payload... [2/2]\n> ")
    print()
    return EthernetFrame(dest_mac, src_mac, data)