import socket
import time
from models.payload.EthernetFrame import EthernetFrame
from models.payload.EthernetData import EthernetData
from models.payload.IPPacket import IPPacket
from models.util import print_brk

class Ping:
  '''
    Encapsulates ping protocol's methods.
      - ping_sent:        Retains sent state of when ping protocol is triggered to allow termination of ping.
      - ping_received:    Retains received state of ping, allowing class to recognise when ping fails.
  '''
  ping_sent = False
  ping_received = False

  def handle_ping(self, ethernet_frame: EthernetFrame, corresponding_socket: socket.socket):
    '''
      Handles received ethernet data.
      If data received is a response to the original ping, print data, else, send a response.
    '''
    ethernet_data: EthernetData = ethernet_frame.data
    
    if (ethernet_data.protocol == "0r" and self.ping_sent): 
      print(f"Ping response data: {ethernet_data.data} [Success]")
      self.ping_received = True

    elif (ethernet_data.protocol == "0r" and not self.ping_sent):
      print(f"Invalid ping response received ({ethernet_data.data}) to uninitiated ping protocol.")

    else:
      print("Ping request received, echoing data...")
      ip_packet: IPPacket = IPPacket(
        dest_ip = ethernet_data.src_ip,
        src_ip = ethernet_data.dest_ip,
        protocol = "0r",
        data = ethernet_data.data
      )
      corresponding_socket.send(bytes(ip_packet.dumps() , "utf-8"))
      print(f"Data ({ethernet_data.data}) echoed.")
  
  def ping(self, ip_packet: IPPacket, corresponding_socket: socket.socket, max_pings: int = 5):
    self.ping_sent = True
    sent_pings = 0

    while not (self.ping_received) and not (sent_pings == max_pings):
      print(f"Pinging {ip_packet.destination} with {ip_packet.data_length} bytes of data...")
      corresponding_socket.send((bytes(ip_packet.dumps(), "utf-8")))
      sent_pings += 1
      time.sleep(1)

    if self.ping_sent and (not self.ping_received) and sent_pings == max_pings:
      print("Ping failed, request timed out. [Failed]")
      print_brk()

    self.ping_sent = False
    self.ping_received = False
