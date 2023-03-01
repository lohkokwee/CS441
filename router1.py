from Router import Router
from constants import ROUTER1_PORT

router = Router("0x1A", "R1", ROUTER1_PORT, 5)
router.run()