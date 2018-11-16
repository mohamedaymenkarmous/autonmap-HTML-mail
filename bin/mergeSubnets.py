#!/usr/bin/python

import os
import netaddr
from netaddr import IPNetwork

dir_path = os.path.dirname(os.path.realpath(__file__))
BaseDir=dir_path+"/.."

with open(BaseDir+"/conf/address_list.txt", "r") as ins:
  iplist =[]
  non_iplist=[]
  for line in ins:
    line=line.strip()
    try:
      ip=IPNetwork(line)
      iplist.append(ip)
    except:
      non_iplist.append(line)
  summary = netaddr.cidr_merge(iplist)
  ins.close()
#  print summary[0]
  f=open(BaseDir+"/conf/do_not_touch_this_file_when_running.txt", "w")
  for line in non_iplist:
    f.write(line+"\n")
  for line in summary:
    f.write(str(line)+"\n")
