function get_cidr
{
 ipcalc -p 1.1.1.1 $1 | sed -n 's/^PREFIX=\(.*\)/\/\1/p'
}
function get_network
{
 ipcalc -n $1 | sed -r 's/^NETWORK=//'
}
probe1_ip=$1
probe1_vlan=$2
probe1_mtu=$3
probe1_address=$4
probe1_mask=$5
probe1_gw=$6
dst_ip=$7
dst_mask=$8
test_protocol=$9
test_port=${10}
let icmp_size=$probe1_mtu-28
probe1_cidr=$(get_cidr $probe1_mask)
dst_cidr=$(get_cidr $dst_mask)
probe1_full_address=${probe1_address}${probe1_cidr}
dst_full_address=${dst_ip}${dst_cidr}
net1=$(get_network $probe1_full_address)
net2=$(get_network $dst_full_address)
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
ssh root@$probe1_ip ip route add $dst_ip/32 via $probe1_gw dev eth1
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
ssh root@$probe1_ip ip route add $dst_ip/32 via $probe1_gw dev eth1.$probe1_vlan
sleep 1
fi
fi
sleep 5
#ssh root@$probe1_ip tracepath -n -m 10 $dst_ip
#sleep 1
#ssh root@$probe1_ip tracepath -n -m 10 $dst_ip
#sleep 1
#ssh root@$probe1_ip tracepath -n -m 10 $dst_ip
#sleep 1
#ssh root@$probe1_ip tracepath -n -m 10 $dst_ip
if [ $test_protocol -eq 1 ];
then
ssh root@$probe1_ip ping $dst_ip -c 4 -W 2 -I $probe1_address -s $icmp_size -M do
status=$?
fi
if [ $test_protocol -eq 2 ];
then
ssh root@$probe1_ip ncat $dst_ip $test_port -v -z 
status=$?
fi
if [ $test_protocol -eq 3 ];
then
ssh root@$probe1_ip ncat $dst_ip $test_port -v -z -u
status=$?
fi
if [ $test_protocol -eq 4 ];
then
ssh root@$probe1_ip dig @$dst_ip vmware.com
status=$?
fi
if [ $test_protocol -eq 5 ];
then
ssh root@$probe1_ip ntpdate -q $dst_ip
status=$?
fi
sleep 1

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