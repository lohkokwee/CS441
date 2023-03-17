import os
from typing import Literal

def print_brk():
  print('-' * os.get_terminal_size().columns)

def print_node_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- (q)uit \t Terminate node.")
  print("- (h)elp \t Display command menu.")
  print("- eth \t Create an ethernet packet.")
  print("- ip \t Create an IP packet.")
  print_brk()

def print_router_int_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()
  
  print("Commands:")
  print("- (q)uit \t Terminate router interface.")
  print("- (h)elp \t Display command menu.")
  print("- arp -a \t Display all ARP tables.")
  print("- arp -n \t Display ARP tables with connected nodes.")
  print("- arp -r \t Display ARP tables with connected router interfaces.")
  print_brk()

def print_command_not_found(device: Literal["node", "router_interface"]):
  print_brk()
  print("Unidentified command. Please use a registered command...")
  if device == "node":
    print_node_help(has_top_break = False)
  else:
    print_router_int_help()


if __name__ == "__main__":
  pass