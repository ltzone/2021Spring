sudo ovs-ofctl add-flow s1 "in_port=s1-eth4 actions=drop"                    # s2 --x-> s1
sudo ovs-ofctl add-flow s2 "in_port=s2-eth1 actions=drop"                    # s1 --x-> s2
echo "Custom Flows Successfully Set"