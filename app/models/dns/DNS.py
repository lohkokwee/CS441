from models.node import Node
from models.dns import DNS

class DNS(Node):
  '''
    A DNS implementation of a node.
  '''

  dns_table = None

  def __init__(
    self,
    node_mac: str,
    router_int_mac: str,
    router_int_port: int,
    router_int_host: str = "localhost",
    records: List[DNSRecord] = None
  ):
    super().__init__(node_mac, router_int_mac, router_int_port, router_int_host)
    self.dns_table = DNS(records)

  