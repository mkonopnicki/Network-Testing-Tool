function get_cidr
{
 ipcalc -p 1.1.1.1 $1 | sed -n 's/^PREFIX=\(.*\)/\/\1/p'
}
function get_network
{
 ipcalc -n $1 | sed -r 's/^NETWORK=//'
}
probe1_ip=$1
probe2_ip=$2
probe1_vlan=$3
probe1_mtu=$4
probe1_address=$5
probe1_mask=$6
probe1_gw=$7
probe2_vlan=$8
probe2_mtu=$9
probe2_address=${10}
probe2_mask=${11}
probe2_gw=${12}
test_protocol=${13}
test_port=${14}
let icmp_size=$probe1_mtu-28
probe1_cidr=$(get_cidr $probe1_mask)
probe2_cidr=$(get_cidr $probe2_mask)
probe1_full_address=${probe1_address}${probe1_cidr}
probe2_full_address=${probe2_address}${probe2_cidr}
net1=$(get_network $probe1_full_address)
net2=$(get_network $probe2_full_address)
if [ "$net1" = "$net2" ];
then
routed=0
else
routed=1
fi
if [ "$probe1_vlan" = "0" ];
then
ssh root@$probe1_ip ifconfig eth1 mtu $probe1_mtu up
sleep 1
ssh root@$probe1_ip ifconfig eth1 $probe1_full_address
if [ $routed -eq 1 ];
then
ssh root@$probe1_ip ip route add $probe2_address/32 via $probe1_gw dev eth1
sleep 1
fi
else
ssh root@$probe1_ip ip link add link eth1 name eth1.$probe1_vlan type vlan id $probe1_vlan
sleep 1
ssh root@$probe1_ip ifconfig eth1 mtu $probe1_mtu up
sleep 1
ssh root@$probe1_ip ifconfig eth1.$probe1_vlan  mtu $probe1_mtu up
sleep 1
ssh root@$probe1_ip ifconfig eth1.$probe1_vlan  $probe1_full_address
sleep 1
if [ $routed -eq 1 ];
then
ssh root@$probe1_ip ip route add $probe2_address/32 via $probe1_gw dev eth1.$probe1_vlan
sleep 1
fi
fi
if [ "$probe2_vlan" = "0" ];
then
ssh root@$probe2_ip ifconfig eth1 mtu $probe2_mtu up
sleep 1
ssh root@$probe2_ip ifconfig eth1 $probe2_full_address
if [ $routed -eq 1 ];
then
ssh root@$probe2_ip ip route add $probe1_address/32 via $probe2_gw dev eth1
sleep 5
ssh root@$probe2_ip tracepath -n -m 10 $probe1_address
sleep 1
ssh root@$probe2_ip tracepath -n -m 10 $probe1_address
sleep 1
ssh root@$probe1_ip tracepath -n -m 10 $probe2_address
sleep 1
ssh root@$probe1_ip tracepath -n -m 10 $probe2_address
fi
else
ssh root@$probe2_ip ip link add link eth1 name eth1.$probe2_vlan type vlan id $probe2_vlan
sleep 1
ssh root@$probe2_ip ifconfig eth1 mtu $probe2_mtu up
sleep 1
ssh root@$probe2_ip ifconfig eth1.$probe2_vlan  mtu $probe2_mtu up
sleep 1
ssh root@$probe2_ip ifconfig eth1.$probe2_vlan  $probe2_full_address
sleep 1
ssh root@$probe2_ip tracepath -n -m 10 $probe1_address
sleep 1
ssh root@$probe2_ip tracepath -n -m 10 $probe1_address
sleep 1
ssh root@$probe1_ip tracepath -n -m 10 $probe2_address
sleep 1
ssh root@$probe1_ip tracepath -n -m 10 $probe2_address
if [ $routed -eq 1 ];
then
ssh root@$probe2_ip ip route add $probe1_address/32 via $probe2_gw dev eth1.$probe2_vlan
sleep 5
ssh root@$probe2_ip tracepath -n -m 10 $probe1_address
sleep 1
ssh root@$probe2_ip tracepath -n -m 10 $probe1_address
sleep 1
ssh root@$probe1_ip tracepath -n -m 10 $probe2_address
sleep 1
ssh root@$probe1_ip tracepath -n -m 10 $probe2_address
fi
fi
if [ $test_protocol -eq 1 ];
then
ssh root@$probe2_ip ping $probe1_address -c 4 -W 2 -I $probe2_address -s $icmp_size -M do
status=$?
fi
if [ $test_protocol -eq 2 ];
then
ssh root@$probe1_ip ncat -l $probe1_address $test_port -v &> /var/log/tcp.log &
sleep 1
ssh root@$probe2_ip ncat $probe1_address $test_port -v -z 
status=$?
sleep 1
ssh root@$probe1_ip pkill -f ncat
fi
if [ $test_protocol -eq 3 ];
then
ssh root@$probe1_ip ncat -l $probe1_address $test_port -v -u &> /var/log/udp.log &
sleep 1
ssh root@$probe2_ip ncat $probe1_address $test_port -v -z -u
sleep 1
ssh root@$probe1_ip pkill -f ncat
grep -i $probe2_address /var/log/udp.log
status=$?
fi
sleep 1
if [ "$probe2_vlan" = "0" ];
then
ssh root@$probe2_ip ifconfig eth1 down
sleep 1
ssh root@$probe2_ip ifconfig eth1 up
else
ssh root@$probe2_ip ip link delete eth1.$probe2_vlan
sleep 1
fi
if [ "$probe1_vlan" = "0" ];
then
ssh root@$probe1_ip ifconfig eth1 down
sleep 1
ssh root@$probe1_ip ifconfig eth1 up
else
ssh root@$probe1_ip ip link delete eth1.$probe1_vlan
sleep 1
fi
exit $status