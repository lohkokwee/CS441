from models.Router import Router
from models.constants import ROUTER1_CONFIG

router = Router(**ROUTER1_CONFIG)
router.run()