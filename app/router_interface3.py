from models.router.RouterInterface import RouterInterface
from config import ROUTER_INT3_CONFIG

router_interface = RouterInterface(**ROUTER_INT3_CONFIG)
router_interface.run()