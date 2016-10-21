import IPy
import logging
import subprocess

limit = 5
white_list = ['127.0.0.1', '0.0.0.0', '192.168.0.0/20', '192.168.10.0/24', '172.17.0.0/16']
get_unsecure_ip = "netstat -atun|awk '{print $5}'|awk -F':' '/^[0-9]/ {print $1}'|sort |uniq -c|awk '$1>%d {print $2}'" %limit
add_ip_iptables = "iptables -I INPUT -p tcp -s {} -j REJECT"
logging.basicConfig(filename='console.log', level=logging.INFO, format='%(asctime)s  %(levelname)s [%(processName)s] '
                                                                       + '[%(threadName)s] - %(message)s')

def iptable(ip):
    subprocess.Popen(add_ip_iptables.format(ip), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def tcp_wrapper(ip):
    with open('/etc/hosts.deny', 'a+') as f:
        f.write('ALL: {}'.format(ip))


def judge(ips):
    all_ips = ips.strip().split('\n')
    print(all_ips)
    for ip in all_ips:
        for inet in white_list:
            if ip in IPy.IP(inet):
                print('{} is Pass'.format(ip))
                break
        else:
            # Deny Unsecured ip
            print('{} is Catch'.format(ip))


if __name__ == '__main__':
    ips, err = subprocess.Popen(get_unsecure_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    judge(ips)

