import os

def make_packet(dest_ip: str, dest_mac: str, src_ip: str, src_mac: str, payload: str) -> str:  
  packet_header = f"{dest_ip}-{dest_mac}-{src_ip}-{src_mac}"
  return f"{packet_header}-{payload}"

def break_packet(packet: str):
  dest_ip, dest_mac, src_ip, src_mac, payload = packet.split("-")
  return dict(
    dest_ip=dest_ip, dest_mac=dest_mac, src_ip=src_ip, src_mac=src_mac, payload=payload
  )

def print_brk():
  print('-' * os.get_terminal_size().columns)

if __name__ == "__main__":
  # print(break_packet("0x2B-0x2A-test2"))
  pass