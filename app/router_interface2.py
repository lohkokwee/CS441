from models.nic.NetworkInterface import NetworkInterface
from config import ROUTER_INT2_CONFIG

router_interface = NetworkInterface(**ROUTER_INT2_CONFIG)
router_interface.run()