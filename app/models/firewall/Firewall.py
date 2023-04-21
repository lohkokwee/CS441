from typing import Dict, List
from models.util import print_brk, print_command_not_found, input_ip_sequence

class Firewall:
  '''
    Firewall implementation to filter packets based on
    1. Packet filtering based on header information
  '''
  blacklist: List[str]
  whitelist: List[str]
  blacklist_disabled: bool
  whitelist_disabled: bool

  def __init__(
    self,
    blacklist: str = [],
    whitelist: str = [],
    blacklist_disabled: bool = False,
    whitelist_disabled: bool = True,
  ):
    self.blacklist = blacklist
    self.whitelist = whitelist
    self.blacklist_disabled = blacklist_disabled
    self.whitelist_disabled = whitelist_disabled

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
    '''
      Returns True if both whitelisting and blacklisting disabled.
      If either enabled, return False.
    '''
    return not (self.blacklist_disabled or self.whitelist_disabled)

  def enable_whitelist(self):
    self.whitelist_disabled = False
    print("Whitelisting firewall successfully enabled.")
    print_brk()

  def disable_whitelist(self):
    self.whitelist_disabled = True
    print("Whitelisting firewall successfully disabled.")
    print_brk()

  def enable_blacklist(self):
    self.blacklist_disabled = False
    print("Blacklisting firewall successfully enabled.")
    print_brk()

  def disable_blacklist(self):
    self.blacklist_disabled = True
    print("Blacklisting firewall successfully disabled.")
    print_brk()

  def get_blacklist(self) -> List:
    return self.blacklist

  def get_whitelist(self) -> List:
    return self.whitelist

  def is_allowed(self, ip_address):
    if not self.blacklist_disabled:
      return not (ip_address in self.blacklist)
    elif not self.whitelist_disabled:
      return not (ip_address in self.whitelist)
    return True
    
  def handle_whitelist_firewall_input(self, device: str, has_top_break: bool = True):
    if has_top_break:
      print_brk()
      
    print("Commands to configure firewall:")
    print("- w \t\t View the current whitelist for this node.")
    print("- w -a \t\t Add a node to the whitelist.")
    print("- w -r \t\t Remove a node from the whitelist.")
    print("- w -d \t Disable firewall.")
    print("- w -e \t Enable firewall.")
    print_brk()

    user_input = input("> ")
    if user_input == "w":
      print(f"Current whitelisted IPs: {self.get_whitelist()}.")
      print_brk()

    elif user_input == "w -a":
      ip_to_add = input_ip_sequence("What is the value of the IP you wish to add to whitelist?\n> ")
      self.add_to_whitelist(ip_to_add)

    elif user_input == "w -r":
      ip_to_add = input_ip_sequence("What is the value of the IP you wish to remove from whitelist?\n> ")
      self.remove_from_whitelist(ip_to_add)

    elif user_input == "w -d":
      self.disable_whitelist()

    elif user_input == "w -e":
      self.enable_whitelist()
    
    else:
      print_command_not_found(device = device)

  def handle_firewall_input(self, has_top_break: bool = True):
    if has_top_break:
      print_brk()

    print("Commands to configure firewall:")
    print("- s \t\t Display current status of firewall.")
    print("- b \t\t View the current blacklist for this node.")
    print("- b -a \t\t Add a node to the blacklist.")
    print("- b -r \t\t Remove a node from the blacklist.")
    print("- b -e \t\t Enable blacklist firewall.")
    print("- b -d \t\t Disable blacklist firewall.")
    print("- w \t\t View the current whitelist for this node.")
    print("- w -a \t\t Add a node to the whitelist.")
    print("- w -r \t\t Remove a node from the whitelist.")
    print("- w -e \t\t Enable whitelist firewall.")
    print("- w -d \t\t Disable whitelist firewall.")
    print_brk()

    user_input = input("> ")

    if user_input == "s":
      print(f"Blacklisting currently enabled: {not self.blacklist_disabled}")
      print(f"Whitelisting currently enabled: {not self.whitelist_disabled}")
      print_brk()

    elif user_input == "b":
      print(f"Current blacklisted IPs are: {self.get_blacklist()}.")
      print_brk()

    elif user_input == "b -a":
      ip_to_add = input_ip_sequence("What is the value of the IP you wish to add to blacklist?\n> ")
      self.add_to_blacklist(ip_to_add)
    
    elif user_input == "b -r":
      ip_to_add = input_ip_sequence("What is the value of the IP you wish to remove from blacklist?\n> ")
      self.remove_from_blacklist(ip_to_add)

    elif user_input == "b -e":
      self.enable_blacklist()

    elif user_input == "b -d":
      self.disable_blacklist()
    
    elif user_input == "w":
      print(f"Current whitelisted IPs: {self.get_whitelist()}.")
      print_brk()

    elif user_input == "w -a":
      ip_to_add = input_ip_sequence("What is the value of the IP you wish to add to whitelist?\n> ")
      self.add_to_whitelist(ip_to_add)

    elif user_input == "w -r":
      ip_to_add = input_ip_sequence("What is the value of the IP you wish to remove from whitelist?\n> ")
      self.remove_from_whitelist(ip_to_add)

    elif user_input == "w -e":
      self.enable_whitelist()

    elif user_input == "w -d":
      self.disable_whitelist()
 
    else:
      print_command_not_found(device = "node")
