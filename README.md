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

3. Upon a successful connection, typing any statement into the node terminals allows you to prepare a packet to the respective client. An example sequence _(between Node2 and Node3)_ can be seen below.
```
    Message to Node3
    Payload: Message to Node3
    Enter destination IP address: 0x2B
    Packet: 0x2B-R2-0x2A-N2-Message to Node3
```

## Note
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

<hr>

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