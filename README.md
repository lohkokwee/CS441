# CS441
CS441 Network Security Project - Python Network Emulator

# Getting Started
<!-- 1. Create a python [virtual environment](https://realpython.com/python-virtual-environments-a-primer/#create-it) and run it. -->

<!-- 2. Install dependencies
```
    pip install requirements.txt
``` -->
> Note: while connecting the nodes/routers interfaces, please wait for a few seconds until you see the horizontal bar and get an indication of completion before you proceed to connect another node - this is to ensure that the ARP routing tables are assigned correctly

1. Open five different terminals and run the commands below in their respective orders for each node. 
```

    python app/router_interface1.py

    or 

    py app/router_interface1.py
```
```
    python app/router_interface2.py

    or

    py app/router_interface2.py
```
```
    python app/node1.py

    or

    py app/node1.py
```
```
    python app/node2.py

    or 

    py app/node2.py
```
```
    python app/node3.py

    or 

    py app/node3.py
```

2. You will notice an ARP routing table being built for the router interfaces in the respective terminals where the node is connecting to.

3. Upon a successful connection, a table of commands will be displayed.
* Command table for nodes:
 ```   
 Commands:
- (q)uit 	 Terminate node.
- (h)elp 	 Display command menu.
- eth 		 Create an ethernet packet.
- ip 		 Create an IP packet.
- dns 		 Display all DNS records.
- arp 		 Display all ARP tables.
- reply 	 Reply ARP broadcast query.
- firewall 	 Read or configure firewall options.
- kill 		 Configure kill protocol options.
- sniff 	 Configure sniffing functionality.
- spoof 	 Spoof your IP address.
- whoami 	 Bring up current ip and mac address.
```
* Command table for router's network interfaces:
```
Commands:
- (q)uit 	 Terminate network interface.
- (h)elp 	 Display command menu.
- reconnect  Attempt to reconnect to failed connections during start up.
- ip route 	 Display all routing tables.
- arp 		 Display all ARP tables.
- arp -n 	 Display ARP tables with connected nodes.
- arp -r 	 Display ARP tables with connected network interfaces.
- whoami 	 Bring up current ip and mac address.
- broadcast  Broadcast an ARP query
```

These commands provide you the entry point to test our various implementations of the networking protocols.


## Important
* When starting `node 2` and `node 3`, make sure `node 2` is fully connected first before starting `node 3`. You should see the following output in the terminal for `router_interface2` before starting `node 3`.
```
    Node connection request received.
    Assigning free IP address... [1/3]
    Requesting MAC address... [2/3]
    Updating ARP tables... [3/3]
    Connection established. [Completed]
```
* When typing `$ arp` command into the terminal for `router_interface2`, you should see the following output
```
    Displaying all ARP tables...
    {
        "0x2A": "N2",
        "0x2B": "N3"
    }
    > ARP tables for with connected network interfaces (IP:MAC).
    {
        "0x11": "R1"
    }
```
* If you don't see the above output, close `node 2` and `node 3` and restart them again, one by one.


# Baseline Features
> Note: the baseline features can be tested via the terminals set up in the getting started section.

## 1. Ethernet Broadcast
Ethernet frames are used as the main mode of communication within a LAN. An ethernet frame can be sent within the LAN through the `eth` command in the `node_<num>.py` terminal. 

The process below demonstrates the example for when `node 2` wishes to send an ethernet frame to `node 3`.

1. Enter `$ eth` into `node 2`'s terminal and fill up the required data from the sequence.
```
Create an ethernet frame by entering the following infomration into the console.
Enter destination MAC address... [1/2]
> N3
Enter payload... [2/2]
> Sending eth frame to N3
Ethernet frame sent. [Completed]
```

2. There will be an indication of a successful frame being sent.
3. `node 3` receives the frame.
```
Ethernet frame received: N3|N2|35|4e:6f:6e:65:2d:4e:6f:6e:65:2d:34:2d:53:65:6e:64:69:6e:67:20:65:74:68:20:66:72:61:6d:65:20:74:6f:20:4e:33
Intended recipient, retrieving data...
Ethernet frame data: Sending eth frame to N3
```

## 2. IP Packet Forwarding
IP packet forwarding enables inter LAN communications. A IP packet can be generated and sent via the `$ ip` command in any `node_<num>.py` terminal.

The process below demonstrates the example for when `node 1` wishes to send a ping to `node 2`.

1. Enter `$ ip` into `node 1`'s terminal and fill up the required data from the sequence.
```
ip
Create a IP packet by entering the following infomration into the console.
Enter destination address...
> 0x2A
--------------------------------------------------------------------------------
Enter protocol...
- 0 	 Ping protocol
- 1 	 Log protocol
- 2 	 Kill protocol
> 0
--------------------------------------------------------------------------------
Enter payload...
> Ping!
```

2. An IP packet with the respective information will be routed throught `R1`.
```
IP packet received:  0x2A|0x1A|0|5|Ping!
Checking IP packet destination... [1/2]
Destination not in LAN.
Routing packet to LAN with destination prefix... [2/2]
IP packet routed. [Completed]
```

3. `R2` receives the IP packet routed from `R1` and encapsulates it to broadcast it to nodes within its LAN.
```
IP packet received:  0x2A|0x1A|0|5|Ping!
Checking IP packet destination... [1/2]
Broadcasting encapsulated IP packets to connected nodes... [2/2]
Broadcasting ethernet frame to connected MACs...
Ethernet frame broadcasted.
```

4. `node 2` recieves the encapsulated packet as an ethernet frame and executes the protocol accordingly.
```
Ethernet frame received: N2|R2|17|30:78:32:41:2d:30:78:31:41:2d:30:2d:50:69:6e:67:21
Intended recipient, retrieving data...
Ping request received, echoing data...
Data (Ping!) echoed.
```

## 3. Protocols
The three protocols are involved in every IP packet communication. These protocols are input as part of the IP packet creation sequence.

### 3.1. Ping
When a node initiates a ping with another node, (in this implementation) by default, 5 pings are sent out until a ping response is received. Two possible scenarios then take place.

1. No response is received and the request times out.
```
Pinging 0x3A with 15 bytes of data...
Pinging 0x3A with 15 bytes of data...
Pinging 0x3A with 15 bytes of data...
Pinging 0x3A with 15 bytes of data...
Pinging 0x3A with 15 bytes of data...
Ping failed, request timed out. [Failed]
```

2. The pinged node responds and the data is echoed, as seen in the example in section 2.

### 3.2. Log
When a node initiates a log with another node, the corresponding node simply logs the data into its respective file.

The process below demonstrates the example for when `node 1` wishes to send a log to `node 2`.

1. Enter `$ ip` into `node 1`'s terminal and fill up the required data from the sequence.
```
ip
Create a IP packet by entering the following infomration into the console.
Enter destination address...
> 0x2A
--------------------------------------------------------------------------------
Enter protocol...
- 0 	 Ping protocol
- 1 	 Log protocol
- 2 	 Kill protocol
> 1
--------------------------------------------------------------------------------
Enter payload...
> Log this data
--------------------------------------------------------------------------------
IP packet sent. [Completed]
```

2. IP packet is routed accordingly thorugh `R1` and `R2`, and `node 2` recieves the encapsulated packet as an ethernet frame and executes the protocol accordingly.

```
Ethernet frame received: N2|R2|25|30:78:32:41:2d:30:78:31:41:2d:31:2d:4c:6f:67:20:74:68:69:73:20:64:61:74:61
Intended recipient, retrieving data...
Log request received, logging data...
Data logged to file at <path_to_folder>/app/log/0x2A.log. [Success]
```

### 3.3. Kill
A kill protocol intiates a sequence to end the processes on the corresponding node.

The process below demonstrates the example for when `node 1` wishes to kill `node 3`.

1. Enter `$ ip` into `node 1`'s terminal and fill up the required data from the sequence.
```
ip
Create a IP packet by entering the following infomration into the console.
Enter destination address...
> 0x2B
--------------------------------------------------------------------------------
Enter protocol...
- 0 	 Ping protocol
- 1 	 Log protocol
- 2 	 Kill protocol
> 2
--------------------------------------------------------------------------------
Enter payload...
> Kill
--------------------------------------------------------------------------------
IP packet sent. [Completed]
```

2. IP packet is routed accordingly thorugh `R1` and `R2`, and `node 3` recieves the encapsulated packet as an ethernet frame and executes the protocol accordingly.
```
Ethernet frame received: N3|R2|16|30:78:32:42:2d:30:78:31:41:2d:32:2d:4b:69:6c:6c
Intended recipient, retrieving data...
Kill request received...
Initiating kill process on node, terminating all active connections...
Connections terminated, node killed.
```

3. `node 3` terminates and all respective connections are killed.

## 4. IP Spoofing

## 5. Sniffing Attack

## 6. Firewall

# Additional features

## 1. ARP request and reply

`router_interface2` wants to update its ARP table, and sends a ARP broadcast

1. On `router_interface2`'s terminal, type `$ broadcast`, followed by the IP address of the MAC it wishes to update.
2. `router_interface2` will send an ARP broadcast within its LAN, and both `node 2` and `node 3` will receive a broadcast query
```
    Who has IP: 0x2A, I am R2
```
3. Since 0x2A is the IP address of `node 2`, typing the command `$ reply` in `node 2`'s terminal will reply with an ARP reply, updating the router's ARP table.
```
    # node2.py

    ARP response sent.
```

```
    # router_interface2.py

    ARP response received, updating ARP table for 0x2A...
    ARP table successfully updated.
```

### 1.1. ARP poisoning

1. During the ARP broadcast and reply process, if `node 3` replies before `node 2`, the `router_interface2` will receive `node 3`'s reply which will result in it's ARP table being poisoned. 

2. You will see the following output when typing the `$ arp` command into `router_interface2`'s terminal.

```
    # router_interface2.py

    Displaying all ARP tables...    
    > ARP tables for with connected 
    nodes (IP:MAC). 
    {
        "0x2A": "N3", 
        "0x2B": "N3"  
    }
    > ARP tables for with connected 
    network interfaces (IP:MAC).    
    {
        "0x11": "R1"  
    }
```

3. Observe that both "0x2A" and "0x2B" is mapped to MAC address "N3" which is the MAC address of `node 3`.

## 2. DNS resolution

1. Open two additional different terminals and run the commands below in their respective orders for each node. 
```
    python app/router_interface3.py

    or 

    py app/router_interface3.py
```
```
    python app/dns_server.py

    or 

    py app/dns_server.py
```

2. Typing command `$ dns` in the terminal of `dns_server` will display the following

```
    # dns_server.py

    Displaying all DNS records...
    {
        "N1.com": "0x1A",
        "www.N2.com": "0x2A",     
        "N3.com": "0x2B"
    }
```

3. `node 1` will attempt to send an IP packet to "N3.com". Notice that before sending the IP packet, typing `$ dns` in the terminal of `node 1` will produce the following
```
    # node1.py
    
    Displaying all 
    local DNS records...
    {}
```

4. During the process of sending the IP packet, `node 1` will attempt to first resolve the domain name locally by checking its local DNS records. Since it is empty, you will observe the following output in the terminals as `node 1` makes a DNS query to `dns_server`, and `dns_server` replies with a DNS response, allowing `node 1` to save the response into its local DNS records.

```
    # node1.py

    Sending DNS query...
    IP packet sent. [Completed]   
    DNS query sent to DNS server at prefix 0x3.  

    Awaiting DNS response... 
    Ethernet frame received: <withheld for brevity>
    Intended recipient, retrieving data... 
    DNS query response received of {"domain_name": "N3.com", "ip_address": "0x2B"}.

    Updating local DNS cache...   
    Local DNS cache updated.      
    
    Destination address of N3.com successfully resolved to IP address of 0x2B.
```
```
    # dns_server.py

    Ethernet frame received: <withheld for brevity>
    Intended recipient, retrieving data...
    DNS query received.
    Preparing DNS response...
    DNS response prepared with DNS record of {'domain_name': 'N3.com', 'ip_address': '0x2B'}.
    IP packet sent. [Completed]
```

5. Subsequently, typing `$ dns` into the terminal of `node 1` will allow you to observe its updated DNS records
```
    # node1.py

    Displaying all local DNS records...
    {
        "N3.com": "0x2B"
    }
```

6. Subsequent IP packets sent from `node 1` to "N3.com" will not send a DNS query to `dns_server` since `node 1` is able to resolve the domain name locally.
```
    # node1.py

    Create a IP packet by entering the following infomration into the console.Enter destination address...
    > N3.com
    Destination address of N3.com successfully resolved to IP address of 0x2B.
```

### 2.1. DNS spoofing

1. In order for a node to spoof the DNS reply, it must satisfy the following conditions
    *  Sniffing is enabled by typing `$ sniff` followed by `$ e`
    * DNS spoofing enabled by typing `$ sniff` followed by `$ es`
    * Malicious node must be in the same LAN as victim node
    * Malicious node must have pre-configured target domain names that he wants to spoof

```
    # node3.py

    Node sniffing is enabled.
    Node is spoofing DNS.
```

2. In this scenario, `node 3` is the mallory. Typing `$ dns` in the terminal of `node 3` will produce the following output in the terminal. Observe that the node will only spoof DNS queries that are attempting to resolve the domain names for "N1.com", "abc.com" and "def.com".
```
    # node3.py

    Displaying all local DNS records...
    {}
    Displaying malicious DNS records...  
    {
        "N1.com": "0x2B",
        "abc.com": "0x2B",
        "def.com": "0x2B"
    }
```

3. `node 2` will now attempt to resolve the domain name for "N1.com", which is the target domain name for `node 3` to spoof.

4. When `node 2` sends an IP packet to "N1.com", `node 3` who is the malicious node will sniff the DNS query being sent out by `node 2` to the DNS server, and reply with it's own malicious DNS response packet. Note that both DNS server and node 3 will send out a DNS response, but `node 2`, the victim, will only save `node 3`'s DNS response.

```
    # node3.py

    Ethernet frame received: <withheld for brevity>
    Sniffing enabled...
    DNS response prepared with DNS record of {'domain_name': 'N1.com', 'ip_address': '0x2B'}.
    IP packet sent. [Completed]
```

```
    # node2.py

    Ethernet frame received: <withheld for brevity>
    Intended recipient, retrieving data...
    DNS query response received of {"domain_name": "N1.com", "ip_address": "0x2B"}.
    Updating local DNS cache...
    Local DNS cache updated.
    Destination address of N1.com successfully resolved to IP address of 0x2B
```

5. Subsequently, checking `node 2`'s DNS records by typing command `$ dns` into the terminal will produce the following output
```
    # node2.py

    Displaying all local DNS records...
    {
        "N1.com": "0x2B"
    }
```

6. Subsequent IP packets sent out by `node 2` to "N1.com" will be routed to IP address "0x2B", which is `node 3`, instead of the correct IP of "0x1A", which is `node 1`.