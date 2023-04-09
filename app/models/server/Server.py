from models.nic.NetworkInterface import NetworkInterface
from config import HOST

class Server(NetworkInterface):
  '''
    Servers implementing router interfaces to relay information to different networks.
    Maintains NetworkInterface's functionality.
  '''
  def __init__(
    self,
    device_name: str,
    network_int_ip_address: str,
    network_int_mac: str,
    network_int_port: int,
    max_connections: int,
    network_int_relay_addresses: list[tuple] = [],
    network_int_host: str = HOST
  ):
    super().__init__(
      device_name,
      network_int_ip_address,
      network_int_mac,
      network_int_port,
      max_connections,
      network_int_relay_addresses, network_int_host
    )
  