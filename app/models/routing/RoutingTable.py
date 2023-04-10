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
    return ":".join(list(dump))

  
  def remove_entire_entry(self, prefix_to_remove: str) -> None:
    self.routing_table.pop(prefix_to_remove, None)
    for neighbour in self.routing_table.keys():
      routes = self.routing_table[neighbour]
      for route in routes:
        prefix, cost = route
        if prefix == prefix_to_remove:
          self.routing_table[neighbour].remove(route)
          break

  def get_next_hop_prefix(self, prefix_to_retrieve: str) -> str:
    '''
      Get next prefix to hop to based on cost.
      1. Checks for immediate network interface IPs first (routing_table's keys)
      2. If not available, check each entry for cheapest and sned to that network interface for next hop.
    '''
    if prefix_to_retrieve in self.routing_table:
      return prefix_to_retrieve
    
    next_hop_prefix = None
    min_cost = float('inf')
    for neighbour_prefix in self.routing_table.keys():
      routes = self.routing_table[neighbour_prefix]      
      for route in routes:
        prefix, cost = route
        if prefix == prefix_to_retrieve and int(cost) < min_cost:
          next_hop_prefix = neighbour_prefix
          min_cost = int(cost)
          break

    return next_hop_prefix

  def pprint(self) -> None:
    print(json.dumps({route: [f"({prefix}, {cost})" for prefix, cost in self.routing_table[route]] for route in self.routing_table}, indent=2))