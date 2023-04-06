from models.router.RouterInterface import RouterInterface
from config import ROUTER_INT1_CONFIG

router_interface = RouterInterface(**ROUTER_INT1_CONFIG)
router_interface.run()