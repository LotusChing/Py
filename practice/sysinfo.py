import subprocess
import platform
import psutil
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

vm_platform_list = ['vmware', 'xen', 'kvm', 'virtualbox', 'hyperv']

'''
    Server Basic Info
'''


def get_os_release():
    return ' '.join(platform.linux_distribution())


def get_manufacturer_name():
    cmd = """dmidecode -q -s system-manufacturer|grep -v '#'"""
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    manufacturer = res.stdout.readline().decode().split(',')[0].split()[0].strip('\n')
    return manufacturer


def get_manufacturer_date():
    cmd = 'dmidecode -q -t bios|grep "Release Date"'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    manufacturer_date = res.stdout.readline().decode().split(': ')[-1].strip('\n')
    t = time.strptime(manufacturer_date, '%m/%d/%Y')
    manufacturer_date = time.strftime('%Y-%m-%d', t)
    return manufacturer_date


def get_server_model():
    cmd = 'dmidecode -q -s system-product-name|grep -v "#"'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    server_model = res.stdout.readline().decode().strip('\n')
    return server_model


def get_server_sn():
    cmd = 'dmidecode -s system-serial-number|grep -v "#"'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    server_sn = res.stdout.readline().decode().strip('\n').strip()
    return server_sn


def get_server_uuid():
    cmd = 'dmidecode -s system-uuid|grep -v "#"'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    server_uuid = res.stdout.readline().decode().strip('\n').strip()
    return server_uuid

'''
    CPU
'''


def get_cpu_model():
    with open('/proc/cpuinfo') as f:
        for item in f.readlines():
            if item.split(': ')[0].strip() == 'model name':
                return item.split(': ')[1].strip('\n')

'''
    Memory
'''


def get_memory_slot_count():
    # 获取总共的插槽
    cmd = 'dmidecode -t 17|grep -v "#" | grep "Size"|wc -l'
    total_slots_count = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return total_slots_count.stdout.readline().decode().strip('\n')


def get_memory_slot_use():
    # 获取已经使用的插槽
    cmd = 'dmidecode -q -t 17|grep -v "#" |grep " MB"|wc -l'
    use_slots_count = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return use_slots_count.stdout.readline().decode().strip('\n')


def use_slots_info():
    # 获取每个插槽内存条大小
    cmd = 'dmidecode -q -t 17 |grep -v "#"|grep " MB"'
    use_slots_data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readlines()
    slots_info_list = [i.decode().split(': ')[1].strip('\n') for i in use_slots_data]
    return slots_info_list


def memory_info(keywords):
    with open('/proc/meminfo') as f:
        for i in f.readlines():
            if i.split(': ')[0] == keywords:
                return int(i.split(': ')[1].split()[0]) // 1024


'''
    Disk
'''


def get_disk_info():
    disk_info_list = []
    cmd = 'fdisk -l|egrep  -v "identifier|mapper"|grep "Disk"'
    disk_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.readlines()
    for item in disk_info:
        if 'bytes' not in item.decode():
            continue
        tmp_dict = {
            'device': item.decode().split()[1].strip(':'),
            'size': int(item.decode().split()[-2])//1024//1024//1024
        }
        disk_info_list.append(tmp_dict)
    return disk_info_list


'''
    NIC
'''


def get_nic_info():
    nic_info_list = []
    black_list = ['lo']
    net_info = psutil.net_if_addrs()
    for nic in net_info:
        if nic in black_list:
            continue
        tmp_dict = {'device': nic}
        for nic_item in net_info[nic]:
            if nic_item.family == 2:
                tmp_dict['address'] = nic_item.address
                tmp_dict['netmask'] = nic_item.netmask
            if nic_item.family == 17:
                tmp_dict['mac'] = nic_item.address
        if len(tmp_dict.keys()) == 4:
            nic_info_list.append(tmp_dict)
    return nic_info_list

if __name__ == '__main__':
    data = {
        'os_release': get_os_release(),
        'hostname': platform.node(),
        'manufacturer_name': get_manufacturer_name(),
        'manufacturer_date': get_manufacturer_date(),
        'server_model': get_server_model(),
        'is_vm': 1 if get_manufacturer_name().lower() in vm_platform_list else 0,
        'sn': get_server_uuid() if get_manufacturer_name().lower() in vm_platform_list else get_server_sn(),
        'uuid': get_server_uuid(),
        'cpu_count': psutil.cpu_count(),
        'cpu_model': get_cpu_model(),
        'memory_slots_count': get_memory_slot_count(),
        'memory_slot_use': get_memory_slot_use(),
        'memory_slot_info': use_slots_info(),
        'memory_size': memory_info('MemTotal'),
        'disk_info': get_disk_info(),
        'nic_info': get_nic_info(),
    }
    pp.pprint(data)
