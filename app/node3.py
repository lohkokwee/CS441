from models.Node import Node
from models.constants import NODE3_CONFIG

node = Node(**NODE3_CONFIG)
node.run()