from models.node.Node import Node
from config import NODE3_CONFIG

node = Node(**NODE3_CONFIG)
node.run()