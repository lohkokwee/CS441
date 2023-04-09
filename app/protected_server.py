from models.nic.NetworkInterface import NetworkInterface
from config import PROTECTED_SERVER_CONFIG

protected_server = NetworkInterface(**PROTECTED_SERVER_CONFIG)
protected_server.run()