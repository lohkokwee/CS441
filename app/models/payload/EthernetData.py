class EthernetData:
  '''
    Processes ethernet data from IP packets.
  '''
  dest_ip: str = None
  src_ip: str = None
  protocol: str = None
  data: str = None

  def __init__(
    self,
    data: str,
  ):
    data_segments = data.split("-") 
    if len(data_segments) == 4:
      # Data used to create ethernet frame was built from IP packet
      self.dest_ip = data_segments[0]
      self.src_ip = data_segments[1]
      self.protocol = data_segments[2]
      self.data = data_segments[3]
    
    else:
      # Ethernet frame created for LAN transmissions (no IP packet data)
      self.data = data
  
  def dumps(self) -> str:
    '''
      Dumps the current EthernetFrame into a str format for transmission.
    '''
    return f"{self.dest_ip}-{self.src_ip}-{self.protocol}-{self.data}"