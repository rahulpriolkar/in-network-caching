table_add MyIngress.ipv4_exact MyIngress.ipv4_forward 10.4.0.1 => 2
table_add MyIngress.ipv4_exact MyIngress.ipv4_forward 10.4.0.2 => 3
table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.0.0/16 => 1
table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.1.0.0/16 => 1
table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.2.0.0/16 => 1
table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.3.0.0/16 => 1
