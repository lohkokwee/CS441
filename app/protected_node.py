from models.node.Node import Node
from config import PROTECTED_NODE_CONFIG

node = Node(**PROTECTED_NODE_CONFIG)
node.run()