# Network Testing Tool v 0.3
1. Overview
    Network Testing Tool is a utility to validate network configuration(mostly firewall) prior to
    deploying any type of software by simulating one or more network hosts using provided configuration.
    Tool is modular and allows to create custom test definitions.
    As of this release this tool is able to perform:
     TCP and UDP port tests using ncat(just connection no data)
     ICMP test using custom size MTU
     DNS test using dig
     NTP test using ntpdate
     PLEASE NOTE THAT in OF THIS VERSION DHCP FUNCTION OF [network_config] section is not working due to bug
2. Components
    There are 2 main components of this tools:  
    * Testing probe - Preconfigured Photon OS 4 virtual machine with 2 virtual NICs(first NIC for ssh connectivity to run tests, and second NIC for test traffic)
        This preconfigured VM is available for download as OVA, however if needed it can be build from scratch.
        When using OVA, by default first interface(ssh) will be configured for DHCP. If no DHCP is available in the environment then first interface can be manually configured with static IP address. Login for OVA root/VMw@re1!
        If tou would like to create your own testing probe using any other Linux distro, following requirments have to be met:
        - installed tools: ncat(from nmap-ncat package), dig, ntpdate, tracepath
        - firewall disabled
        - 2nd NIC device name -  eth1
        - ssh login for root user allowed
        - ssh keys for machine where testing script will be run added as trusted

    * Testing script - Python script which will perform all the tests by connecting to testing probes using SSH. 
        For ease of use preconfigured VM using Photon OS 4 is available for download as OVA. This preconfigured instance has got all the necessary prerequistes installed, as well as SSH keys configured for password-less access to testing probe VMs. By default first interface will be configured for DHCP. If no DHCP is available in the environment then first interface can be manually configured with static IP address. Login for OVA root/VMw@re1!
        Testing script with some sample modules is already available on this appliance in path /ntt
        Download link for OVAs:
        https://1drv.ms/u/s!AvvI6hs2QM7khOoCJ2ym1c4XLgFB8A?e=LdPAzh
        

3. Running Network Testing Tool
    
 This testing tool consists of following files:
 * ntt.py - Python script that runs the test with the name of module json file as parameter(eg. "python3 ntt.py module-vcf.json") 
 * module file in json format - file that contains test definitions
 * config file in json format - file which is delivered together with module that needs to be filled with networking details
 * test-dst.sh - auxilliary bash script to perform tests
 * test-src-dst.sh - auxilliary bash script to perform tests
    All file have to be place in the same folder
   Appropriate file permissions have to be assigned to all file so they can be accessed and executed.

4. Customizing Module File
- General:
    * "description" - text description to be display and logged in to file when running test
    * "config_file_name" - name of the json file containing configuration
- Entities(this section contains definitions of all the network hosts that will be simulated):
    * "name" - name of the entity to be matched with "src_entity" or "dst_entity" in test definition
    * "network_config" - name of the section in config file that contains network details for each simulated entity
    * "probe_mapping" - name of the probe mapping label present in config file (to allow for easier probe swapping)
- Existing_entities (this section contains definitions of all already existing infrastrcutre servers, they can only be used in dst type test)
    * "name" - name of the entity to be matched with "dst_entity" in  "dst" test definition
    * "network_config" - name of the section in config file that contains network details for one or more existing server
- Test definitions:
    * "name" - text description to be display and logged in to file
    * "type" - type of test to be conducted
        "src_dst"
        Test where both source and destination are simulated by testing probe
        supported protocols:TCP,UDP, ICMP
        "dst"
        Test where only source is simulated by testing probe
        supported protocols:TCP, UDP(unreliable since there is no way to confirm delivery), ICMP, DNS, NTP
    * "optional"  - (true/false) 
    If set to "false" then test is always performed(mandatory)
    If set to "true" then additional parameters have to be added to determine if test will be performed:
    "optional_parameter" - name of the parameter in the config file
    "optional_parameter_value" - value of the parameter in the config file
    If all conditions are met then test will be performed.
    * "src_entity" - name of the source for test, needs to match one of the names in section [entities] of module file 
    * "dst"entity" - name of the destination for test for type "src_dst" needs to match one of the names in section [entities] of module file or
    for type "dst" needs to match one of the names in section [existing_entities] in module file
    * "reverse_flow" - defines if test will be run 2nd time with reversed source and destination(only available for type "src_dst")
    * "flows" - this section contains list of one or more flows to be performed as part of a test. "protocol" and in case of TCP/UDP
    "port" values have to be specified for each flow 
    5. Customizing Config File:
    - deploy: - this section cover the network details for testing probes
        * "name" - name of the testing probe to match section [probe_mapping]
        * "mgt_ip_address" - ip address of eth0 on testing probe VMs
    - probe_mapping: - map probe label from module file section [probe_mapping] with name from [deploy] section of config file
    - network_config:
        * "name" - to match name from [existing_entities] section of module file
        * "dhcp" - true/false to get DHCP address for eth1 for simulated host(not working in this version, will be reintroduced in next release)
        * "vlan" - vlan tag for desired network, use 0 for untagged traffic
        * ip/mask/gw - IP information for simulated host
        * MTU - MTU size for interface, currently only used in ICMP test
        Please note that for sections defined in module file under [existing_entities] only "name" "ip" and "mask" neeed to be defined. If more then one server
        is present in each sections connection testes will be performed on all of them.
    - additional parameter can be added here to be used with "optional" parameter in test definition

