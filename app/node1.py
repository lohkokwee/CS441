from models.Node import Node
from models.constants import NODE1_CONFIG

node = Node(**NODE1_CONFIG)
node.run()