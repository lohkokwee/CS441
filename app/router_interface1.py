from models.nic.NetworkInterface import NetworkInterface
from config import ROUTER_INT1_CONFIG

router_interface = NetworkInterface(**ROUTER_INT1_CONFIG)
router_interface.run()