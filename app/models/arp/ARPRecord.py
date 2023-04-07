import socket
from typing import TypedDict, Union

class ARPRecord(TypedDict):
  '''
    ARPRecord can have no socket connections if it resides in a node. Only sends layer 3 data to router interfaces.
  '''
  mac: str
  corresponding_socket: Union[socket.socket, None] 