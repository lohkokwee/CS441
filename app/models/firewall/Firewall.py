from typing import Dict, List
from models.util import print_brk, print_command_not_found

class Firewall:
  '''
    Firewall implementation to filter packets based on
    1. Packet filtering based on header information
  '''
  blacklist: List[str]
  whitelist: List[str]
  disabled: bool

  def __init__(
    self,
    blacklist: str = [],
    whitelist: str = [],
    disabled: bool = False,
  ):
    self.blacklist = blacklist
    self.whitelist = whitelist
    self.disabled = disabled

  def __str__(self) -> str:
    return

  def add_to_blacklist(self, ip_add: str):
    if ip_add not in self.blacklist:
      self.blacklist.append(ip_add)
      print(f"IP {ip_add} successfully added to blacklist.")
    else:
      print("IP already in blacklist.")
    print_brk()

  def remove_from_blacklist(self, ip_add: str):
    if ip_add in self.blacklist:
      self.blacklist.remove(ip_add)
      print(f"IP {ip_add} removed from blacklist.")
    else:
      print("IP is currently not in blacklist.")
    print_brk()

  def add_to_whitelist(self, ip_add: str):
    if ip_add not in self.whitelist:
      self.whitelist.append(ip_add)
      print(f"IP {ip_add} successfully added to whitelist.")
    else:
      print("IP already in whitelist.")
    print_brk()

  def remove_from_whitelist(self, ip_add: str):
    if ip_add in self.whitelist:
      self.whitelist.remove(ip_add)
      print(f"IP {ip_add} removed from whitelist.")
    else:
      print("IP is currently not in whitelist.")
    print_brk()
  
  def is_disabled(self):
    return self.disabled

  def enable_firewall(self):
    self.disabled = False
    print("Firewall successfully enabled.")
    print_brk()

  def disable_firewall(self):
    self.disabled = True
    print("Firewall successfully disabled.")
    print_brk()

  def get_blacklist(self) -> List:
    return self.blacklist

  def get_whitelist(self) -> List:
    return self.whitelist
  
  def input_ip_sequence(self, prompt: str) -> str:
    ip_to_add = input(prompt)
    valid_input = True if ip_to_add[:2] == "0x" else False
    while not valid_input:
      ip_to_add = input("Invalid input, please enter a valid IP (e.g., 0x1A).\n> ")
      valid_input = True if ip_to_add[:2] == "0x" else False
    
    return ip_to_add
  
  def handle_firewall_input(self, has_top_break: bool = True):
    if has_top_break:
      print_brk()

    print("Commands to configure firewall:")
    print("- b \t\t View the current blacklist for this node.")
    print("- b -a \t\t Add a node to the blacklist.")
    print("- b -r \t\t Remove a node from the blacklist.")
    print("- w \t\t View the current whitelist for this node.")
    print("- w -a \t\t Add a node to the whitelist.")
    print("- w -r \t\t Remove a node from the whitelist.")
    print("- (d)isable \t Disable firewall.")
    print("- (e)nable \t Enable firewall.")
    print_brk()

    user_input = input("> ")

    if user_input == "b":
      print(f"Current blacklisted IPs are: {self.get_blacklist()}.")
      print_brk()

    elif user_input == "b -a":
      ip_to_add = self.input_ip_sequence("What is the value of the IP you wish to add to blacklist?\n> ")
      self.add_to_blacklist(ip_to_add)
    
    elif user_input == "b -r":
      ip_to_add = self.input_ip_sequence("What is the value of the IP you wish to remove from blacklist?\n> ")
      self.remove_from_blacklist(ip_to_add)
    
    elif user_input == "w":
      print(f"Current whitelisted IPs: {self.get_whitelist()}.")
      print_brk()

    elif user_input == "w -a":
      ip_to_add = self.input_ip_sequence("What is the value of the IP you wish to add to whitelist?\n> ")
      self.add_to_whitelist(ip_to_add)

    elif user_input == "w -r":
      ip_to_add = self.input_ip_sequence("What is the value of the IP you wish to remove from whitelist?\n> ")
      self.remove_from_whitelist(ip_to_add)

    elif user_input == "disable" or user_input == "d":
      self.disable_firewall()

    elif user_input == "enable" or user_input == "e":
      self.enable_firewall()
    
    else:
      print_command_not_found(device = "node")
