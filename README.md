# CS441
CS441 Network Security Project - Python Network Emulator

# Getting Started
<!-- 1. Create a python [virtual environment](https://realpython.com/python-virtual-environments-a-primer/#create-it) and run it. -->

<!-- 2. Install dependencies
```
    pip install requirements.txt
``` -->

1. Open five different terminals and run the commands below in their respective orders for each node (two for routers, three for nodes).
```
    python app/router1.py
```
```
    python app/router2.py
```
```
    python app/node1.py
```
```
    python app/node2.py
```
```
    python app/node3.py
```

2. You will notice an ARP table being built for the routers in their respective where each node is connecting.

3. Upon a successful connection, typing any statement into the node terminals allows you to prepare a packet to the respective client.
