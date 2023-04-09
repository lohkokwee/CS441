from typing import Dict, Union, List
import json

class RoutingTable:
  '''
    Determines the sequential layer 3 hops that a network interface is connected to.
  '''
  routing_table: Dict[str, List[tuple[str, int]]] = None
  
  def __init__(self):
    self.routing_table = {}
  
  def create_entry(self, network_interface_prefix: str) -> None:
    self.routing_table[network_interface_prefix] = []

  def extend_entry(self, network_interface_prefix: str, prefix_to_extend: str, cost: int) -> None:
    self.routing_table[network_interface_prefix].append((prefix_to_extend, cost))

  def loads(self, own_network_interface_prefix: str, network_interface_prefix: str, routing_table_dump: str):
    '''
      Loads routing table from a routing_table_dump.
    '''
    print(f"---> Loading dumps: {routing_table_dump}")
    if not network_interface_prefix in self.routing_table:
      self.routing_table[network_interface_prefix] = []

    if routing_table_dump:
      for route in routing_table_dump.split(":"):
        prefix, cost = route.split(",")
        if (prefix != own_network_interface_prefix):
          self.routing_table[network_interface_prefix].append((prefix, cost))

  def dumps(self):
    '''
      Dumps entire routing table as a single string.
    '''
    
    dump = set()
    for prefix in self.routing_table:
      dump.add(f"{prefix},1")
      for inner_prefix, cost in self.routing_table[prefix]:
        if not inner_prefix in self.routing_table: # Add only if don't have a shorter path
          dump.add(f"{inner_prefix},{int(cost) + 1}")
    print(f"---> Routing table dumps: {dump}")
    return ":".join(list(dump))

  
  def remove_entire_entry(self, prefix_to_remove: str) -> None:
    self.routing_table.pop(prefix_to_remove, None)
    for neighbour in self.routing_table.keys():
      routes = self.routing_table[neighbour]
      for route in routes:
        prefix, cost = route
        if prefix == prefix_to_remove:
          self.routing_table[neighbour].remove(route)
  
  def remove_from_entry(self, network_interface_prefix: str, prefix_to_remove: str) -> None:
    for entry in self.routing_table[network_interface_prefix]:
      prefix, cost = entry
      if prefix == prefix_to_remove:
        self.routing_table[network_interface_prefix].remove(entry)
        break

  def get_route():
    pass

  def pprint(self) -> None:
    print(json.dumps({route: [f"({prefix}, {cost})" for prefix, cost in self.routing_table[route]] for route in self.routing_table}, indent=2))