from models.node.Node import Node
from config import NODE1_CONFIG

node = Node(**NODE1_CONFIG)
node.run()