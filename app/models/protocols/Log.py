import os
import pathlib
import logging
from datetime import datetime
from models.payload.EthernetFrame import EthernetFrame

class Log:
  '''
    Encapsulates log protocol's methods.
  '''

  @staticmethod
  def log(ethernet_frame: EthernetFrame) -> bool:
    print("Log request received, logging data...")

    log_filename = f"./log/{ethernet_frame.data.dest_ip}.log"
    log_format = "%(asctime)s - %(message)s"
    
    os.makedirs(os.path.dirname(log_filename), exist_ok=True) # Create file directory if doesnt exist
    logging.basicConfig(
      filename = log_filename,
      filemode = "a",
      format = log_format,
      level = logging.INFO
    )

    logger = logging.getLogger()
    logger.info(f"[src_ip: {ethernet_frame.data.src_ip}] {ethernet_frame.data.data}")

    log_path = pathlib.Path(os.path.abspath(__file__))
    print(f"Data logged to file at {log_path.parent.parent.parent}{log_filename[1:]}. [Success]")

    return True