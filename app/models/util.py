import os
from typing import Literal

def encode_data(data: str) -> str:
  '''
    Returns encoded string in hexadecimal (string) format.
  '''
  return ':'.join(f"{ord(ch):02x}" for ch in data)

def decode_data(data: str) -> str:
  '''
    Returns decoded hexadecimal (string) in readable (string) format.
  '''
  return ''.join([chr(int(ch, 16)) for ch in data.split(":")])

def print_brk():
  print('-' * os.get_terminal_size().columns)

def print_node_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- (q)uit \t Terminate node.")
  print("- (h)elp \t Display command menu.")
  print("- eth \t\t Create an ethernet packet.")
  print("- ip \t\t Create an IP packet.")
  print("- arp \t\t Display all ARP tables.")
  print("- reply \t Reply ARP broadcast query.")
  print("- firewall \t Read or configure firewall options.")
  print("- kill \t\t Configure kill protocol options.")
  print("- sniff \t Configure sniffing functionality.")
  print("- whoami \t Bring up current ip and mac address.")
  print_brk()

def print_router_int_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- (q)uit \t Terminate router interface.")
  print("- (h)elp \t Display command menu.")
  print("- arp \t\t Display all ARP tables.")
  print("- arp -n \t Display ARP tables with connected nodes.")
  print("- arp -r \t Display ARP tables with connected router interfaces.")
  print("- whoami \t Bring up current ip and mac address.")
  print("- broadcast \t Broadcast an ARP query")
  print_brk()

def print_command_not_found(device: Literal["node", "router_interface"]):
  print_brk()
  print("Unidentified command. Please use a registered command...")
  if device == "node":
    print_node_help(has_top_break = False)
  elif device == "router_interface":
    print_router_int_help(has_top_break = False)

if __name__ == "__main__":
  pass