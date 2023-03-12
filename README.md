# CS441
CS441 Network Security Project - Python Network Emulator

# Getting Started
<!-- 1. Create a python [virtual environment](https://realpython.com/python-virtual-environments-a-primer/#create-it) and run it. -->

<!-- 2. Install dependencies
```
    pip install requirements.txt
``` -->
_(Note: while connecting the nodes/routers interfaces, please wait for a few seconds until you see the horizontal bar and get an indication of completion before you proceed to connect another node - this is to ensure that the ARP routing tables are assigned correctly)_

1. Open five different terminals and run the commands below in their respective orders for each node. 
```
    python app/router_interface1.py
```
```
    python app/router_interface2.py
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

2. You will notice an ARP routing table being built for the router interfaces in the respective terminals where the node is connecting to.

3. Upon a successful connection, typing any statement into the node terminals allows you to prepare a packet to the respective client. An example sequence _(between Node2 and Node3)_ can be seen below.
```
    Message to Node3
    Payload: Message to Node3
    Enter destination IP address: 0x2B
    Packet: 0x2B-R2-0x2A-N2-Message to Node3
```