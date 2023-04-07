from models.dns.DNS import DNS
from config import DNS_SERVER_CONFIG

dns_server = DNS(**DNS_SERVER_CONFIG)
dns_server.run()