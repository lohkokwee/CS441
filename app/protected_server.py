from models.servers.Server import Server
from config import PROTECTED_SERVER_CONFIG

protected_server = Server(**PROTECTED_SERVER_CONFIG)
protected_server.run()