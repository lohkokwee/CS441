from typing import TypedDict

class DNSRecord(TypedDict):
  '''
      Single DNS record. Records stored as dictionary for extension. (e.g. TTL)
  '''
  domain_name: str
  ip_address: str