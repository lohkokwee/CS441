import os
from models.arp.ARPTable import ARPTable
from models.util import print_brk, print_command_not_found

class Kill:
  '''
    Encapsulates kill protocol's methods.
    Receipient needs to opt in for kill protocol to be elligible to be killed by sender.
  '''
  is_killable: bool = True
  
  def show_status(self) -> None:
    if self.is_killable:
      print("Node is killable.")
    else:
      print("Node is not killable.")
    print_brk()

  def enable_kill_protocol(self) -> None:
    self.is_killable = True
    print("Kill protocol successfully enabled.")
    print_brk()

  def disable_kill_protocol(self) -> None:
    self.is_killable = False
    print("Kill protocol successfully disabled.")
    print_brk()

  def handle_kill_protocol_input(self, has_top_break: bool = True):
    if has_top_break:
      print_brk()

    print("Commands to configure kill protocol:")
    print("- (s)tatus \t Shows if node is killable.")
    print("- (d)isable \t Disable kill protocol.")
    print("- (e)nable \t Enable kill protocol.")
    print_brk()

    user_input = input("> ")

    if user_input == "status" or user_input == "s":
      self.show_status()

    elif user_input == "disable" or user_input == "d":
      self.disable_kill_protocol()

    elif user_input == "enable" or user_input == "e":
      self.enable_kill_protocol()

    else:
      print_command_not_found(device = "node")

  def kill(self, arp_table: ARPTable) -> None:
    print("Kill request received...")

    if self.is_killable:
      print("Initiating kill process on node, terminating all active connections...")
      connected_sockets = arp_table.get_all_sockets()
      for corresponding_socket in connected_sockets:
        corresponding_socket.close()
      print("Connections terminated, node killed.")
      os._exit(0)

    print("Kill protocol not enabled on node.")


