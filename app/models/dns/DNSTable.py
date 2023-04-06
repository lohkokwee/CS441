from typing import Dict, TypedDict, Union, List
import socket
import json

class DNSTable:
  '''
    Implementation of DNS table. Handles all mutations to DNS table.
  '''

  class DNSRecord(TypedDict):
    '''
      Single DNS record. Records stored as dictionary for extension. (e.g. TTL)
    '''
    domain_name: str
    ip_address: str
  
  resolution_table: Dict(str, DNSRecord) = None

  def __init__(self, records: List[DNSRecord] = None):
    self.resolution_table = {}
    for record in records:
      self.update_resolution_table(record)

  def update_resolution_table(self, record: DNSRecord):
    self.resolution_table[record["domain_name"]] = record
  

  
