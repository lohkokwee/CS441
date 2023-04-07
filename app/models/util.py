import os
import re
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

def is_valid_domain_name(address: str) -> bool:
  regex = "^((?!-)[A-Za-z0-9-]" + "{1,63}(?<!-)\\.)" + "+[A-Za-z]{2,6}"
  pattern = re.compile(regex)
  if (address == None):
    return False
  return (re.search(pattern, address))

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
  print("- dns \t\t Display all DNS records.")
  print("- arp \t\t Display all ARP tables.")
  print("- reply \t Reply ARP broadcast query.")
  print("- firewall \t Read or configure firewall options.")
  print("- kill \t\t Configure kill protocol options.")
  print("- sniff \t Configure sniffing functionality.")
  print("- spoof \t Spoof your IP address.")
  print("- whoami \t Bring up current ip and mac address.")
  print_brk()

def print_router_int_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- (q)uit \t Terminate router interface.")
  print("- (h)elp \t Display command menu.")
  print("- reconnect \t Attempt to reconnect to failed connections during start up.")
  print("- arp \t\t Display all ARP tables.")
  print("- arp -n \t Display ARP tables with connected nodes.")
  print("- arp -r \t Display ARP tables with connected router interfaces.")
  print("- whoami \t Bring up current ip and mac address.")
  print("- broadcast \t Broadcast an ARP query")
  print_brk()

def print_dns_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- (q)uit \t Terminate router interface.")
  print("- (h)elp \t Display command menu.")
  print("- dns \t\t Display all DNS records.")
  print("- arp \t\t Display ARP tables with connected router interfaces.")
  print("- whoami \t Bring up current ip and mac address.")
  print_brk()

def print_command_not_found(device: Literal["node", "router_interface"]):
  print_brk()
  print("Unidentified command. Please use a registered command...")
  if device == "node":
    print_node_help(has_top_break = False)
  elif device == "router_interface":
    print_router_int_help(has_top_break = False)
  elif device == "dns":
    print_dns_help(has_top_break = False)

def print_error(has_top_break: bool = True):
  if has_top_break:
    print_brk()
  print("Process aborted.")
  print_brk()


def input_ip_sequence(prompt: str) -> str:
    ip_to_add = input(prompt)
    valid_input = True if ip_to_add[:2] == "0x" else False
    while not valid_input:
      ip_to_add = input("Invalid input, please enter a valid IP (e.g., 0x1A).\n> ")
      valid_input = True if ip_to_add[:2] == "0x" else False
    
    return ip_to_add

def clean_ethernet_payload(eth_payload: str) -> str:
  '''
    Clean payload for failure case e.g.,
    - 0x1A spoof as 0x2A -> send ping to 0x2B
    - Example of corrupted eth frame = N3|R2|X|dataN3|R2|X|dataN3|R2|X|data...
  '''
  eth_payload = "|".join(eth_payload.split("|")[:4])
  if not eth_payload[-2:].isdigit():
    eth_payload = eth_payload[:-2]
  return eth_payload

def clean_ip_payload(ip_payload: str) -> str:
  '''
    Clean payload for failure case e.g.,
    - 0x1A spoof as 0x2A -> send ping to 0x2B
    - Example of corrupted packet = 0x2A|0x2B|0r|4|test0x2A|0x2B|0r|4|test...
  '''
  ip_payload = "|".join(ip_payload.split("|")[:5])
  if ip_payload[-4:-3] == "0x":
    ip_payload = ip_payload[:-4]
  return ip_payload


if __name__ == "__main__":
  pass