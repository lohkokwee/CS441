from typing import Dict

class Firewall:
  '''
    Firewall implementation to filter packets based on
    1. Packet filtering based on header information
  '''

  whitelist: Dict[str, str]
  blacklist: Dict[str, str]

  def __init__(
    self,
  ):
    self.rule_table = {}

  def __str__(self) -> str:
    return

  def add_rule(self):
    return

  def remove_rule(self):
    return
  
  def disable_firewall(self):
    return

  