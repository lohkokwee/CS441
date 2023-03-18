from models.util import print_brk, print_command_not_found

class Sniffer:
  '''
    Encapsulates sniffing functionality.
  '''
  is_sniffing = False

  def show_status(self) -> None:
    if self.is_sniffing:
      print("Node sniffing is enabled.")
    else:
      print("Node sniffing is disabled.")
    print_brk()
      

  def enable_sniffing(self) -> None:
    self.is_sniffing = True
    print("Sniffing successfully enabled.")
    print_brk()

  def disable_sniffing(self) -> None:
    self.is_sniffing = False
    print("Sniffing successfully disabled.")
    print_brk()

  def handle_sniffer_input(self, has_top_break: bool = True):
    if has_top_break:
      print_brk()

    print("Commands to configure sniffer:")
    print("- (s)tatus \t Shows if sniffing has been activated.")
    print("- (d)isable \t Disable sniffing.")
    print("- (e)nable \t Enable sniffing.")
    print_brk()

    user_input = input("> ")

    if user_input == "status" or user_input == "s":
      self.show_status()

    elif user_input == "disable" or user_input == "d":
      self.disable_sniffing()

    elif user_input == "enable" or user_input == "e":
      self.enable_sniffing()

    else:
      print_command_not_found(device = "node")
