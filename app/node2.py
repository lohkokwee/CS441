from models.node.Node import Node
from config import NODE2_CONFIG

node = Node(**NODE2_CONFIG)
node.run()