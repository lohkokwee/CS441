from models.node.Node import Node
from models.constants import NODE2_CONFIG

node = Node(**NODE2_CONFIG)
node.run()