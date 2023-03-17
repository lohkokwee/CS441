import os
from typing import Literal

def print_brk():
  print('-' * os.get_terminal_size().columns)

def print_node_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- quit \t\t Terminate node.")
  print("- eth \t\t Create an ethernet packet.")
  print("- ip \t\t Create an IP packet.")
  # todo: implement arp broadcast reply
  print("- reply \t\t Reply ARP broadcast query.")
  print("- whoami \t Bring up current ip and mac address.")
  print("- help \t\t Bring up command menu.")
  print_brk()

def print_router_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- quit \t\t Terminate router.")
  print("- whoami \t Bring up current ip and mac address.")
  print("- arp \t\t Bring up current ARP table.")
  # todo: implement arp broadcast
  print("- broadcast \t Broadcast an ARP query")
  print("- help \t\t Bring up command menu.")
  print_brk()

def print_command_not_found(device: Literal["node", "router_interface"]):
  print_brk()
  print("Unidentified command. Please use a registered command...")
  if device == "node":
    print_node_help(has_top_break = False)
  elif device == "router_interface":
    print_router_help(has_top_break = False)

if __name__ == "__main__":
  pass