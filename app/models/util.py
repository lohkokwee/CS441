import os
from typing import Literal

def print_brk():
  print('-' * os.get_terminal_size().columns)

def print_node_help(has_top_break: bool = True):
  if has_top_break:
    print_brk()

  print("Commands:")
  print("- quit \t Terminate node.")
  print("- eth \t Create an ethernet packet.")
  print("- ip \t Create an IP packet.")
  print("- help \t Bring up command menu.")
  print_brk()

def print_command_not_found(device: Literal["node", "router_interface"]):
  print_brk()
  print("Unidentified command. Please use a registered command...")
  if device == "node":
    print_node_help(has_top_break = False)

if __name__ == "__main__":
  pass