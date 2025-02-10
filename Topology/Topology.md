
The core MPLS network interconnects multiple routers, forming a highly redundant and scalable
topology for efficient packet forwarding.

The topology consists of:


+ Provider Edge (PE) Routers (PE1 and PE2): These routers act as gateways between
the MPLS backbone and customer networks. They connect to Customer Edge (CE)
routers via OSPF Area 0, ensuring routing isolation and hierarchical OSPF design.
+ P Routers (P1, P2, P3, and P4): These core routers participate in MPLS label
switching, forwarding traffic across the MPLS backbone.
+ Customer Edge (CE) Routers (CE1 and CE2): These routers serve as entry points
for customer networks, connected to end devices (PC1 and PC2) via subnets
192.168.10.0/24 and 192.168.20.0/24, respectively.
+ Internet Gateway (IGW): The IGW router provides external connectivity, imple-
menting NAT (Network Address Translation) for outbound internet access via in-
terface e0/1.


This topology ensures efficient routing, high availability, and scalability for enterprise
networking solutions by leveraging MPLS label switching, OSPF hierarchical design, and
redundancy mechanisms
