from models.Router import Router
from models.constants import ROUTER2_CONFIG

router = Router(**ROUTER2_CONFIG)
router.run()