from models.router.RouterInterface import RouterInterface
from models.constants import ROUTER_INT2_CONFIG

router_interface = RouterInterface(**ROUTER_INT2_CONFIG)
router_interface.run()