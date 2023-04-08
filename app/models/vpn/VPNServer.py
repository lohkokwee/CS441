from models.router.RouterInterface import RouterInterface

class VPNServer(RouterInterface):
  
  def __init__(self, router_int_ip_address, router_int_mac, router_int_port, max_connections):
    super().__init__(router_int_ip_address, router_int_mac, router_int_port, max_connections)