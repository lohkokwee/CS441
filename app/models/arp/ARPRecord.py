from typing import TypedDict
import socket

class ARPRecord(TypedDict):
  '''
    ARPRecord can have no socket connections if it resides in a node. Only sends layer 3 data to router interfaces.
  '''
  mac: str
  corresponding_socket: socket.socket | None