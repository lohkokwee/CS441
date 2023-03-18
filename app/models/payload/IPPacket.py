from __future__ import annotations
from models.payload.EthernetFrame import EthernetFrame
from models.util import print_brk

class IPPacket:
  '''
    Layer 3 communications can be used to send payloads across/within LANs.
  '''

  destination: str = None
  source: str = None
  protocol: str = None
  data_length: int = None
  data: str = None

  def __init__(
    self,
    dest_ip: str,
    src_ip: str,
    protocol: str,
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
      Data is loaded into EthernetFrame's EthernetData (with IP headers).
    '''
    data_with_headers = f"{self.destination}-{self.source}-{self.protocol}-{self.data}"
    return EthernetFrame(dest_mac, src_mac, data_with_headers)

  @staticmethod
  def input_sequence(src_ip: str) -> IPPacket:
    '''
      Initiates sequence to create IPPacket object.
    '''
    print_brk()
    print("Create a IP packet by entering the following infomration into the console.")
    dest_ip = input("Enter destination IP address... [1/3]\n> ")
    while dest_ip[:2] != "0x":
      dest_ip = input("Destination IP address invalid. Please enter destination IP address again... [1/3]\n> ")

    protocol = input("Enter protocol... [2/3]\n- 0 \t Ping protocol\n- 1 \t Log protocol\n- 2 \t Kill protocol\n> ")
    while not (protocol.isdigit()) or not (int(protocol) in range(3)):
      protocol = input("Invalid protocol, please enter protocol again... [2/3]\n- 0 \t Ping protocol\n- 1 \t Log protocol\n- 2 \t Kill protocol\n> ")

    data = input("Enter payload... [3/3]\n> ")
    return IPPacket(dest_ip, src_ip, protocol, data)