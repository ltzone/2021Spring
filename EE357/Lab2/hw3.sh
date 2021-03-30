# Solution 1, drop any package between s1 and s2, break the loop by dropping one link
# sudo ovs-ofctl add-flow s1 "in_port=s1-eth4 actions=drop"                    # s2 --x-> s1
# sudo ovs-ofctl add-flow s2 "in_port=s2-eth1 actions=drop"                    # s1 --x-> s2
# echo "Custom Flows Successfully Set"

# Solution 2, set flow rules on s2 and s3, break the loop by not using one link
sudo ovs-ofctl add-flow s2 "in_port=s2-eth1 actions=s2-eth2"                    # s1 -> s2 -> h2
sudo ovs-ofctl add-flow s3 "in_port=s3-eth1 actions=s3-eth2"                    # s1 -> s3 -> h3
sudo ovs-ofctl add-flow s2 "in_port=s2-eth2 actions=s2-eth1"                    # h2 -> s2 -> s1
sudo ovs-ofctl add-flow s3 "in_port=s3-eth2 actions=s3-eth1"                    # h3 -> s3 -> s1
echo "Custom Flows Successfully Set"

