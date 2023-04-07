from typing import Dict, TypedDict, Union, List
import json
from .DNSRecord import DNSRecord

class DNSTable:
  '''
    Implementation of DNS table. Handles all mutations to DNS table.
  '''
  
  resolution_table: Dict[str, DNSRecord] = None

  def __init__(self, dns_records: List = None):
    self.resolution_table = {}
    for dns_record in dns_records or []:
      self.update_resolution_table(DNSRecord(domain_name=dns_record["domain_name"],ip_address=dns_record["ip_address"]))

  def update_resolution_table(self, dns_record: DNSRecord):
    self.resolution_table[dns_record["domain_name"]] = dns_record
  
  def resolve(self, domain_name: str) -> DNSRecord:
    '''
      Retrieves DNS record form resolution_table.
    '''
    return self.resolution_table.get(domain_name, None)

  def remove_record(self, domain_name: str) -> bool:
    return bool(self.resolution_table.pop(domain_name, False))

  def pprint(self) -> None:
    print(json.dumps({
      self.resolution_table[domain_name]["domain_name"]: self.resolution_table[domain_name]["ip_address"] for domain_name in self.resolution_table}, 
      indent=2
    ))
