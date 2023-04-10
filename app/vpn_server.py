from models.servers.VPNServer import VPNServer
from config import VPN_SERVER_CONFIG

vpn_server = VPNServer(**VPN_SERVER_CONFIG)
vpn_server.run()