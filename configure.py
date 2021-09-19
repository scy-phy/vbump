#!/usr/bin/env python3

# Nils, SUTD, 2018
from pwn import ssh
import csv
import sys

class DummyLog:
    """Dummy Logging (instead of remote connection)"""
    log = 'conflog'
    fh = None

    def sendline(self, text):
        self.fh.write(text + '\n')

    def __init__(self, ip, port, name):
        self.fh = open(name, 'w')
        self.sendline('! new conf for %s:%d' % (ip, port))

# todo: actually turn this into an object, keep state internally, switch
# modes if required


def createVLAN(id):
    return '''vlan database
vlan add %d
exit''' % (id)

# def deleteVLAN(id):
#    return ='vlan database\nvlan delete %d\nexit\n'%id


def enableVLAN(interface, vlanid):
    return '''configure
interface 1/%d
vlan participation include %d
exit\nexit''' % (interface, vlanid)


def disableVLAN(interface, vlanid):
    return '''configure\ninterface 1/%d
vlan participation exclude %d
exit\nexit''' % (interface, vlanid)


def tagVLAN(interface, vlanid):
    return '''configure
interface 1/%d
vlan tagging %d enable
exit\nexit''' % (interface, vlanid)


def setPVID(interface, vlanid):
    return '''configure
interface 1/%d
vlan pvid %d
exit\nexit''' % (interface, vlanid)


def enableRing(interface, vlanid):
    return '''configure
interface 1/%d
voice vlan dot1p 255 
voice vlan vlan-id 0 
voice vlan auth 
voice vlan data priority trust 
voice vlan disable 
no link-loss-alert operation 
port-monitor condition speed-duplex speed hdx-10 fdx-10 hdx-100 fdx-100 fdx-1000 
power-state 
exit\nexit''' % (interface)


def applyConf(fname, ips, remote):

    conf = {}
    with open(fname) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            if not row['Switch'] in conf:
                conf[row['Switch']] = {}  # a dict of all ports
            # Switch,Slot,Port,PVID,Untagged VLAN,Tagged VLAN
            # csw1,1,1,1,1,
            if row['Untagged VLAN']:
                untagged = [int(i) for i in row['Untagged VLAN'].split(',')]
            else:
                untagged = []
            if row['Tagged VLAN']:
                tagged = [int(i) for i in row['Tagged VLAN'].split(',')]
            else:
                tagged = []
            conf[row['Switch']][int(row['Port'])] = {'pvid': int(row['PVID']), 'untagged': untagged, 'tagged': tagged}
    print(conf)
    for switch in conf:
        print('now handling switch %s'%switch)
        ip = ips[switch]
        if remote:
            s = ssh(host=ip, user='admin', password='private')
            l = s.listen_remote()
            a = remote(s.host, l.port)
            b = l.wait_for_connection()
        else:
            a = DummyLog(ip, 22, switch+fname.replace('csv', 'log'))
        a.sendline('enable')
        allVlans = {}
        # ideally find good way how to clear config without losing remote
        # connection
        for port in conf[switch]:
            # Create all VLANs
            for vlan in conf[switch][port]['untagged']:
                allVlans[vlan] = True
            for vlan in conf[switch][port]['tagged']:
                allVlans[vlan] = True
        for vlan in allVlans:
            a.sendline(createVLAN(vlan))
        # For each port, set PVID, Tagged and untagged VLANs
        for port in conf[switch]:
            a.sendline(setPVID(port, conf[switch][port]['pvid']))
            for vlan in conf[switch][port]['untagged']:
                a.sendline(enableVLAN(port, vlan))
            for vlan in conf[switch][port]['tagged']:
                a.sendline(enableVLAN(port, vlan))
                a.sendline(tagVLAN(port, vlan))


# hard-coded dict for IPs
ips = {'switch1': '10.0.1.1', 'switch2': '10.0.2.1', 'csw1': '172.16.5.1', 'tsw1':'172.16.2.1'}
remote = False
fname = 'conf_test2.csv'
if len(sys.argv)>1:
    fname = sys.argv[1]
applyConf(fname, ips, remote)
