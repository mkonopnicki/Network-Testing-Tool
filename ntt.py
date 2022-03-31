import json
from selectors import EpollSelector
import subprocess
import time
import sys
import datetime
now = datetime.datetime.now()
tsfile = now.strftime("%d-%m-%Y-%H-%M-%S")
ts = now.strftime("%d/%m/%Y %H:%M:%S ")
def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

#class for output logging
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("ntt-log-%s.log" % (tsfile), "a" )
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        pass    
#enabling logging
sys.stdout = Logger()
#loading module file - static name module.json
module_file = sys.argv[1]
with open (module_file) as f:
    module = json.load(f)
    f.close()
#loading module config file based on value from module.json
config_file = module['config_file_name']
with open (config_file) as f:
    config = json.load(f)
    f.close()
    #function to get probe based testing entity details
def get_entity(entity_name):
    for entity in module['entities']:
        if entity['name'] == entity_name:  
            probe_name = entity['probe_mapping']
            probe_deploy = config['probe_mapping'][probe_name]
            for probe in config['deploy']:
                if probe['name'] == probe_deploy:
                    probe_ip = probe['mgt_ip_address']
            network_config_name = entity['network_config']
            for netconfig in config['network_config']:
                if netconfig['name'] == network_config_name:
                    entity_vlan = netconfig['vlan']
                    entity_ip = netconfig['ip']
                    entity_gw = netconfig['gw']
                    entity_mask = netconfig['mask']
                    entity_mtu = netconfig['mtu']
    class entity:
        probe = probe_ip
        vlan = entity_vlan
        ip = entity_ip
        gw = entity_gw
        mask = entity_mask
        mtu = entity_mtu
    return(entity)
    #end of function

    #Function to print test results
def print_test_result(result,res_src_ip, res_dst_ip, res_protocol, res_port=""):
        now = datetime.datetime.now()
        ts = now.strftime("%d/%m/%Y %H:%M:%S ")
        if result == False:
            if res_port:
                print(colored(255, 122, 122, '%sTesting connectivity from %s to %s using %s on port %s failed\n' % (ts,res_src_ip, res_dst_ip, res_protocol,res_port)))
            else:
                print(colored(255, 122, 122, '%sTesting connectivity from %s to %s using %s failed\n' % (ts,res_src_ip, res_dst_ip, res_protocol)))
        if result == True:
            if res_port:
                print(colored(0, 255, 0, '%sTesting connectivity from %s to %s using %s on port %s was successful\n' % (ts,res_src_ip, res_dst_ip, res_protocol, res_port)))
            else:
                print(colored(0, 255, 0, '%sTesting connectivity from %s to %s using %s was successful\n' % (ts,res_src_ip, res_dst_ip, res_protocol)))  
    #end of function

        #Function to print running test
def print_test(tst_src_ip, tst_dst_ip, tst_protocol, tst_port=""):
            now = datetime.datetime.now()  
            ts = now.strftime("%d/%m/%Y %H:%M:%S ")
            if tst_port:
                print(colored(178, 102, 255,'%sTesting connectivity from %s to %s using protocol %s on port %s' % (ts,tst_src_ip, tst_dst_ip, tst_protocol, tst_port))) 
            else:   
                print(colored(178, 102, 255,'%sTesting connectivity from %s to %s using protocol %s' % (ts,tst_src_ip, tst_dst_ip, tst_protocol))) 
    #end of function




#main function
print(colored(153, 204, 255, "\nNetwork Testing Tool v0.3\n"))
print(colored(153, 204, 255, "Writing to log file: ntt-log-%s.log\n" % (tsfile)))
time.sleep(1)
print(colored(204, 102, 0, module['description']))
time.sleep(2)
for test in module['tests']:
    if test['optional'] == True:
        optional_param = test['optional_parameter']
        optional_param_val = test['optional_parameter_value']
        if optional_param_val != config[optional_param]:
            continue

    print(colored(153, 153, 255,'\nStarting Test:%s' % (test['name'])))
    if test['type'] == 'src_dst':
            src_entity = get_entity(test['dst_entity'])
            dst_entity = get_entity(test['src_entity'])
            for flow in test['flows']:
                if flow['protocol'] == "ICMP":
                    test_protocol = 1
                    test_port = ""
                    now = datetime.datetime.now()
                    ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                    print(colored(178, 102, 255, '%sTesting connectivity from %s to %s using ICMP' % (ts,dst_entity.ip, src_entity.ip))) 
                if flow['protocol'] == "TCP":
                    test_protocol = 2
                    test_port = flow['port']
                    now = datetime.datetime.now()
                    ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                    print(colored(178, 102, 255,'%sTesting connectivity from %s to %s using protocol %s on port %s' % (ts,dst_entity.ip, src_entity.ip, flow['protocol'], test_port)))
                if flow['protocol'] == "UDP":
                    test_protocol = 3
                    test_port = flow['port']
                    now = datetime.datetime.now()  
                    ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                    print(colored(178, 102, 255,'%sTesting connectivity from %s to %s using protocol %s on port %s' % (ts,dst_entity.ip, src_entity.ip, flow['protocol'], test_port)))    
                command = subprocess.Popen(['./test-src-dst.sh %s %s %s %s %s %s %s %s %s %s %s %s %d %s ' % (src_entity.probe, dst_entity.probe, src_entity.vlan ,src_entity.mtu, src_entity.ip, src_entity.mask, src_entity.gw, dst_entity.vlan, dst_entity.mtu, dst_entity.ip, dst_entity.mask, dst_entity.gw, test_protocol, test_port )], shell = True)
                command.wait()
                returncode = command.poll()
                if returncode == 0:
                    print_test_result(True,dst_entity.ip,src_entity.ip,flow['protocol'],test_port)
                else:
                    print_test_result(False,dst_entity.ip,src_entity.ip,flow['protocol'],test_port)
            if test['reverse_flow'] == True:
                src_entity = get_entity(test['src_entity'])
                dst_entity = get_entity(test['dst_entity'])
                for flow in test['flows']:
                    if flow['protocol'] == "ICMP":
                        test_protocol = 1
                        test_port = ""
                        now = datetime.datetime.now()
                        ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                        print(colored(178, 102, 255, '%sTesting connectivity from %s to %s using ICMP' % (ts,dst_entity.ip, src_entity.ip))) 
                    if flow['protocol'] == "TCP":
                        test_protocol = 2
                        test_port = flow['port']
                        now = datetime.datetime.now()
                        ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                        print(colored(178, 102, 255,'%sTesting connectivity from %s to %s using protocol %s on port %s' % (ts,dst_entity.ip, src_entity.ip, flow['protocol'], test_port)))
                    if flow['protocol'] == "UDP":
                        test_protocol = 3
                        test_port = flow['port']
                        now = datetime.datetime.now()  
                        ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                        print(colored(178, 102, 255,'%sTesting connectivity from %s to %s using protocol %s on port %s' % (ts,dst_entity.ip, src_entity.ip, flow['protocol'], test_port)))    
                    command = subprocess.Popen(['./test-src-dst.sh %s %s %s %s %s %s %s %s %s %s %s %s %d %s ' % (src_entity.probe, dst_entity.probe, src_entity.vlan ,src_entity.mtu, src_entity.ip, src_entity.mask, src_entity.gw, dst_entity.vlan, dst_entity.mtu, dst_entity.ip, dst_entity.mask, dst_entity.gw, test_protocol, test_port )], shell = True)
                    command.wait()
                    returncode = command.poll()
                    if returncode == 0:
                        print_test_result(True,dst_entity.ip,src_entity.ip,flow['protocol'],test_port)
                    else:
                        print_test_result(False,dst_entity.ip,src_entity.ip,flow['protocol'],test_port)


    if test['type'] == 'dst':
         src_entity = get_entity(test['src_entity'])
         for existing_entity in module['existing_entities']:
            if existing_entity['name'] == test['dst_entity']:
                existing_entity_section = existing_entity['config_section']
                for server in config[existing_entity_section]:
                    for flow in test['flows']:
                        if flow['protocol'] == "ICMP":
                            test_protocol = 1
                            test_port = None
                            now = datetime.datetime.now()
                            ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                            print(colored(178, 102, 255, '%sTesting connectivity from %s to %s using ICMP' % (ts,src_entity.ip, server['ip'])))
                        if flow['protocol'] == "TCP":
                            test_protocol = 2
                            test_port = flow['port']
                            now = datetime.datetime.now()
                            ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                            print(colored(178, 102, 255, '%sTesting connectivity from %s to %s using TCP on port %s' % (ts,src_entity.ip, server['ip'], flow['port'])))
                        if flow['protocol'] == "UDP":
                            test_protocol = 3
                            test_port = flow['port']
                            now = datetime.datetime.now()
                            ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                            print(colored(178, 102, 255, '%sTesting connectivity from %s to %s using UDP on port %s' % (ts,src_entity.ip, server['ip'], flow['port'])))
                        if flow['protocol'] == "DNS":
                            test_protocol = 4
                            test_port = None
                            now = datetime.datetime.now()
                            ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                            print(colored(178, 102, 255, '%sTesting connectivity from %s to %s using DNS' % (ts,src_entity.ip, server['ip'])))
                        if flow['protocol'] == "NTP":
                            test_protocol = 5
                            test_porn = None
                            now = datetime.datetime.now()
                            ts = now.strftime("%d/%m/%Y %H:%M:%S ")
                            print(colored(178, 102, 255, '%sTesting connectivity from %s to %s using NTP' % (ts,src_entity.ip, server['ip'])))
                        command = subprocess.Popen(['./test-dst.sh %s %s %s %s %s %s %s %s %d %s ' % (src_entity.probe, src_entity.vlan ,src_entity.mtu, src_entity.ip, src_entity.mask, src_entity.gw, server['ip'], server['mask'], test_protocol, test_port )], shell = True)
                        command.wait()
                        returncode = command.poll()
                        if returncode == 0:
                            print_test_result(True,src_entity.ip,server['ip'],flow['protocol'],test_port)
                        else:
                            print_test_result(False,src_entity.ip,server['ip'],flow['protocol'],test_port)





