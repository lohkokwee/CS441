from __future__ import annotations
from models.payload.EthernetFrame import EthernetFrame
from models.util import print_brk

class IPPacket:
  '''
    Layer 3 communications can be used to send payloads across/within LANs.
  '''

  destination: str = None
  source: str = None
  protocol: int = None
  data_length: int = None
  data: str = None

  def __init__(
    self,
    dest_ip: str,
    src_ip: str,
    protocol: int,
    data: str
  ):
    self.destination = dest_ip
    self.source = src_ip
    self.protocol = protocol
    self.data_length = len(data)
    self.data = data

  def dumps(self) -> str:
    '''
      Dumps the current IPPacket into a str format for transmission.
    '''
    return f"{self.destination}|{self.source}|{self.protocol}|{self.data_length}|{self.data}"

  @staticmethod
  def loads(data: str) -> IPPacket:
    '''
      Receives IPPacket in a dumped (str) format from IPPacket.dump() and loads an IPPacket object.
    '''
    dest_ip, src_ip, protocol, data_length, data = data.split("|")
    return IPPacket(dest_ip, src_ip, protocol, data)

  def is_recipient(self, ip_address: str) -> bool:
    if ip_address == self.destination:
      return True
    return False

  def dest_ip_prefix(self) -> str:
    return self.destination[:3]

  def to_eth_frame(self, dest_mac: str, src_mac: str) -> EthernetFrame:
    '''
      Converts IP packet (layer 3) to ethernet frame (layer 2) for transmissions within the LAN.
      Destination and source mac are resolved with ARP tables.
    '''
    data_with_protocol = f"{self.protocol}-{self.data}"
    return EthernetFrame(dest_mac, src_mac, data_with_protocol)

  @staticmethod
  def input_sequence(src_ip: str) -> IPPacket:
    '''
      Initiates sequence to create IPPacket object.
    '''
    print_brk()
    print("Create a IP packet by entering the following infomration into the console.")
    dest_ip = input("Enter destination IP address... [1/3]\n> ")
    print()
    protocol = input("Enter protocol... [2/3]\n- 0\t Ping protocol\n- 1\t Log protocol\n- 2\t Kill protocol\n> ")
    print()
    data = input("Enter payload... [3/3]\n> ")
    print()
    return IPPacket(dest_ip, src_ip, protocol, data)