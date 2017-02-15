from tkinter import *
from tkinter import ttk
import random
import os
import re
import socket
import sys
import netmiko
import time


def remove_return(entry):
	tmp = entry.rstrip('\n')
	return tmp

def get_ip (input):
	return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))

def read_doc (file_name):
	for line in open(file_name, 'r').readlines():
		if get_ip(line):
			for each in get_ip(line): 
				#print (each)
				my_devices.append(each)

def to_doc(file_name, varable):
	f=open(file_name, 'a')
	f.write(varable)
	f.write('\n')
	f.close()
				

my_devices = []				
username = sys.argv[1]
password = sys.argv[2]
ftp_server = sys.argv[3]
file_name = sys.argv[4]
read_doc ('dev list.txt')
for ip in my_devices:
	try:
		print (ip)
		ip = remove_return(ip)
		net_connect = netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password) 
		file_to_download = 'ftp://'+ftp_server+'/'+file_name
		file_to_download = 'copy ' + file_to_download + ' flash:/'+file_name+'\n'+'\n'+'\n'+'\n'
		print (file_to_download)
		arp = net_connect.send_command(file_to_download)
		temp1 = net_connect.send_command('\n'+'\n'+'\n'+'\n')
		#sleep (300)
		#print ('arp '+arp)
		arp = net_connect.send_command_expect('verify flash:'+file_name)
		#print (arp)
		pass_ver = arp.index('hash verification successful')
		if pass_ver > 0:
			print ("IOS verified")
			net_connect.send_command('conf t')
			net_connect.send_command('no boot system')
			net_connect.send_command('boot system flash:'+file_name)
			net_connect.send_command('exit')
			ver = net_connect.send_command('show run | i boot')
			if 'boot system flash:'+file_name in ver:
				print ('boot system flash:'+file_name)
				ver = net_connect.send_command('write mem')
				status = ip + ", has been updated"
				print (ip +" has been updated")
				to_doc('Status.csv',status)
			else:
				print ('boot system flash:'+file_name)
				status = ip + ", has failed"
				print (ip +" has failed")
				to_doc('Status.csv',status)
	except:
		temp = (ip + ", has failed")
		to_doc('Status.csv',temp)