def make_packet(dest_ip: str, src_ip: str, payload: str) -> str:  
  packet_header = f"{dest_ip}-{src_ip}"
  return f"{packet_header}-{payload}"

def check_packet():
  return ""