from models.server.Server import Server
from config import VPN_SERVER_CONFIG

vpn_server = Server(**VPN_SERVER_CONFIG)
vpn_server.run()