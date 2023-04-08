from models.dns.DNSServer import DNSServer
from config import DNS_SERVER_CONFIG

dns_server = DNSServer(**DNS_SERVER_CONFIG)
dns_server.run()