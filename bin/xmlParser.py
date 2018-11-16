#!/usr/bin/python

from lxml import etree
import json
import os

# Directory of this file
dir_path = os.path.dirname(os.path.realpath(__file__))
# Base directory of this project
BaseDir=dir_path+"/.."

# Check the parameters file
data = None
with open(BaseDir+'/conf/parameters.json') as parameters_json:
  try:
    # Load the JSON file
    data = json.load(parameters_json)
  except ValueError as e:
    print('The file conf/parameters.json is invalid: %s' % e)
    quit()

# The parameters should exist
if data is None:
  print "No config file was found"
  quit()

# From email
From=data["From"]
# To email
To=data["To"]
# Notify always after scan is finished whatever the result
NotifyAlwaysAfterScanIsFinished=data["NotifyAlwaysAfterScanIsFinished"]
# Notify if new host up is detected
NotifyIfNewHostUpIsDetected=data["NotifyIfNewHostUpIsDetected"]
# Notify if new host down is detected
NotifyIfNewHostDownIsDetected=data["NotifyIfNewHostDownIsDetected"]
# Notify if new port up is detected
NotifyIfNewPortUpIsDetected=data["NotifyIfNewPortUpIsDetected"]
# Notify if new port down is detected
NotifyIfNewPortDownIsDetected=data["NotifyIfNewPortDownIsDetected"]
# Notify if new hostname is detected
NotifyIfNewHostnameIsDetected=data["NotifyIfNewHostnameIsDetected"]
# Notify if new os info is detected
NotifyIfNewOSInfoIsDetected=data["NotifyIfNewOSInfoIsDetected"]
# Show new host up
ShowNewHostUp=data["ShowNewHostUp"]
# Show new host down
ShowNewHostDown=data["ShowNewHostDown"]
# Show new port up
ShowNewPortUp=data["ShowNewPortUp"]
# Show new port down
ShowNewPortDown=data["ShowNewPortDown"]
# Show new hostname info
ShowNewHostnameInfo=data["ShowNewHostnameInfo"]
# Show new os info
ShowNewOSInfo=data["ShowNewOSInfo"]

# For each notification parameter, if it's set to true, we define a '\n'
# So the autonmap.sh file can detect if there is extra lines and the mail notification will be processed
NotifyAlwaysAfterScanIsFinishedStr=""
if NotifyAlwaysAfterScanIsFinished and NotifyAlwaysAfterScanIsFinished=="true":
  NotifyAlwaysAfterScanIsFinishedStr="\n"
NotifyIfNewHostUpIsDetectedStr=""
if NotifyIfNewHostUpIsDetected and NotifyIfNewHostUpIsDetected=="true":
  NotifyIfNewHostUpIsDetectedStr="\n"
NotifyIfNewHostDownIsDetectedStr=""
if NotifyIfNewHostDownIsDetected and NotifyIfNewHostDownIsDetected=="true":
  NotifyIfNewHostDownIsDetectedStr="\n"
NotifyIfNewPortUpIsDetectedStr=""
if NotifyIfNewPortUpIsDetected and NotifyIfNewPortUpIsDetected=="true":
  NotifyIfNewPortUpIsDetectedStr="\n"
NotifyIfNewPortDownIsDetectedStr=""
if NotifyIfNewPortDownIsDetected and NotifyIfNewPortDownIsDetected=="true":
  NotifyIfNewPortDownIsDetectedStr="\n"
NotifyIfNewHostnameIsDetectedStr=""
if NotifyIfNewHostnameIsDetected and NotifyIfNewHostnameIsDetected=="true":
  NotifyIfNewHostnameIsDetectedStr="\n"
NotifyIfNewOSInfoIsDetectedStr=""
if NotifyIfNewOSInfoIsDetected and NotifyIfNewOSInfoIsDetected=="true":
  NotifyIfNewOSInfoIsDetectedStr="\n"

# Verification of the existance of the scan-prev.xml file
try:
  scanPrev = etree.parse(BaseDir+"/logs/scan-prev.xml")
  if scanPrev is None or len(scanPrev.xpath("/nmaprun"))==0:
    print "Aucun scan n'est effectue. Verifiez que le fichier logs/scan-prev.xml est cree"
    quit()
except IOError:
  print "Verifiez que le fichier logs/scan-prev.xml est cree"
  quit()

# Verification of the existance of the ndiff-prev.xml file
try:
  ndiff = etree.parse(BaseDir+"/logs/ndiff-prev.xml")
except IOError:
  ndiff=None

# List that will contain all the scan result row in the HTML table
scan_result_array_json=[]

# XML Scan Tree : /nmaprun
nmaprun=scanPrev.xpath("/nmaprun")
# XML Scan Tree : /nmaprun/host
hosts=nmaprun[0].xpath("host")
#startTime = nmaprun[0].get("start")
#endTime = nmaprun[0].xpath("runstats/finished")[0].get("time")
# Scan start time in text format
startTimeStr = nmaprun[0].get("startstr")
# Scan end time in text format
endTimeStr = nmaprun[0].xpath("runstats/finished")[0].get("timestr")
# Scan duration Time in text format
duration = nmaprun[0].xpath("runstats/finished")[0].get("elapsed")

# If this is not the first scan :
# -- The ndiff file exists
# -- And
# -- The XML Ndiff Tree exists : /nmapdiff/scandiff/hostdiff
if ndiff is not None and ndiff.xpath("/nmapdiff/scandiff/hostdiff"):
  # Looping for each node in the XML Ndiff Tree : /nmapdiff/scandiff/hostdiff
  for hostdiff in ndiff.xpath("/nmapdiff/scandiff/hostdiff"):
    # Object that represents one row that contains a result line in the HTML table
    scan_result_obj_json={}
    # Host node if this host is always available from the previous scan
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/host
    host=hostdiff.xpath("host")
    # Host node if this host comes available from the previous scan
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/b/host
    hostAdded=hostdiff.xpath("b/host")
    # Host node if this host comes unavailable from the previous scan
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/a/host
    hostRemoved=hostdiff.xpath("a/host")
    # CSS Style of this current row
    trStyle=""
    # If this node is always available from the previous scan
    if len(host)>0:
      # The common variable name that contains the host node
      host=host[0]
      # The CSS Style of this current row (default)
      scan_result_obj_json['tr_style']=""
    # If this node becomes available from the previous scan
    elif len(hostAdded)>0:
      # The common variable name that contains the host node
      host=hostAdded[0]
      # A prepended string that will be set when generating the HTML row table
      scan_result_obj_json['prepend']=NotifyIfNewHostUpIsDetectedStr
      # The CSS Style of this current row (green color)
      scan_result_obj_json['tr_style']=" style='color:green'"
    # If this node becomes unavailable from the previous scan
    elif len(hostRemoved)>0:
      # The common variable name that contains the host node
      host=hostRemoved[0]
      # A prepended string that will be set when generating the HTML row table
      scan_result_obj_json['prepend']=NotifyIfNewHostDownIsDetectedStr
      # The CSS Style of this current row (red color)
      scan_result_obj_json['tr_style']=" style='color:red'"
    # Extraction of the host IP Address
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/address[addr]
    address=host.xpath("address")[0].get("addr")

    # Ports number Array of the current host
    portArray=[]
    # Ports state Array of the current host
    portStateArray=[]
    # Ports service Array of the current host
    portServiceArray=[]
    # Ports service version Array of the current host
    portVersionArray=[]
    # Ports type Array of the current host
    portTypeArray=[]

    # Unmodified ports
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port
    ports=host.xpath("ports/port")
    # For each port related to the curretn host in the ndiff file
    for port in ports:
      # If the node port state exists
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port/state
      if len(port.xpath("state"))>0:
        # Appending the port number/protocol to the port number array
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port[portid]
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port[protocol]
        portArray.append(port.get("portid")+"/"+port.get("protocol"))
        # Appending the port state to the port state array
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port/state[state]
        portStateArray.append(port.xpath("state")[0].get("state"))
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port/service
        portService=port.xpath("service")
        # If the port service node exists
        if len(portService)>0:
          # Appending the port service to the port service array
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port/service[name]
          portServiceArray.append(portService[0].get("name"))
          # The variable that will contains the port service version
          portVersion=""
          # If the attribute product exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port/service[product]
          if portService[0].get("product"):
            # Adding the product attribute to the variable that will be stored later
            portVersion=portVersion+portService[0].get("product")+" "
          # If the attribute version exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port/service[version]
          if portService[0].get("version"):
            # Adding the version attribute to the variable that will be stored later
            portVersion=portVersion+portService[0].get("version")+" "
          # If the attribute extrainfo exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/port/service[extrainfo]
          if portService[0].get("extrainfo"):
            # Adding the extrainfo attribute to the variable that will be stored later
            portVersion=portVersion+"("+portService[0].get("extrainfo")+") "
          # Appending the port service version to the port service version array
          portVersionArray.append(portVersion)
        # If the port service does not exist
        else:
          # Resetting of the port service array
          portServiceArray.append("")
          # Resetting of the port service version array
          portVersionArray.append("")
        # The detected port is the same from the previous nmap scan
        portTypeArray.append('same')
      # If the node port state does not exists
      else:
        # Nothing to do because the state of the port is not known
        continue

    # Modified ports (added from the previous scan)
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port
    ports=host.xpath("ports/portdiff/b/port")
    # For each modified port
    for port in ports:
      # If the port service node exists
      if len(port.xpath("state"))>0:
        # Appending the port number/protocol to the port number array
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port[portid]
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port[protocol]
        portArray.append(port.get("portid")+"/"+port.get("protocol"))
        # Appending the port state to the port state array
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port/state[state]
        portStateArray.append(port.xpath("state")[0].get("state"))
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port/service
        portService=port.xpath("service")
        # If the port service node exists
        if len(portService)>0:
          # Appending the port service to the port service array
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port/service[name]
          portServiceArray.append(portService[0].get("name"))
          # The variable that will contains the port service version
          portVersion=""
          # If the attribute product exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port/service[product]
          if portService[0].get("product"):
            # Adding the product attribute to the variable that will be stored later
            portVersion=portVersion+portService[0].get("product")+" "
          # If the attribute version exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port/service[version]
          if portService[0].get("version"):
            # Adding the version attribute to the variable that will be stored later
            portVersion=portVersion+portService[0].get("version")+" "
          # If the attribute extrainfo exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/b/port/service[extrainfo]
          if portService[0].get("extrainfo"):
            # Adding the extrainfo attribute to the variable that will be stored later
            portVersion=portVersion+"("+portService[0].get("extrainfo")+") "
          # Appending the port service version to the port service version array
          portVersionArray.append(portVersion)
        # If the port service does not exist
        else:
          # Resetting of the port service array
          portServiceArray.append("")
          # Resetting of the port service version array
          portVersionArray.append("")
        # The detected port is a new port that doesn't existed in the previous nmap scan
        portTypeArray.append('added')
      # If the node port state does not exists
      else:
        # Nothing to do because the state of the port is not known
        continue

    # Modified ports (removed from the previous scan)
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port
    ports=host.xpath("ports/portdiff/a/port")
    # For each modified port
    for port in ports:
      # If the port service node exists
      if len(port.xpath("state"))>0:
        # Appending the port number/protocol to the port number array
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port[portid]
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port[protocol]
        portArray.append(port.get("portid")+"/"+port.get("protocol"))
        # Appending the port state to the port state array
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port/state[state]
        portStateArray.append(port.xpath("state")[0].get("state"))
        # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port/service
        portService=port.xpath("service")
        # If the port service node exists
        if len(portService)>0:
          # Appending the port service to the port service array
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port/service[name]
          portServiceArray.append(portService[0].get("name"))
          # The variable that will contains the port service version
          portVersion=""
          # If the attribute product exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port/service[product]
          if portService[0].get("product"):
            # Adding the product attribute to the variable that will be stored later
            portVersion=portVersion+portService[0].get("product")+" "
          # If the attribute version exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port/service[version]
          if portService[0].get("version"):
            # Adding the version attribute to the variable that will be stored later
            portVersion=portVersion+portService[0].get("version")+" "
          # If the attribute extrainfo exists
          # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/ports/portdiff/a/port/service[extrainfo]
          if portService[0].get("extrainfo"):
            # Adding the extrainfo attribute to the variable that will be stored later
            portVersion=portVersion+"("+portService[0].get("extrainfo")+") "
          # Appending the port service version to the port service version array
          portVersionArray.append(portVersion)
        # If the port service does not exist
        else:
          # Resetting of the port service array
          portServiceArray.append("")
          # Resetting of the port service version array
          portVersionArray.append("")
        # The detected port is a new port that disappeared from the previous nmap scan
        portTypeArray.append('removed')
      # If the node port state does not exists
      else:
        # Nothing to do because the state of the port is not known
        continue

    # Ports already found for the current host
    portsFinished=[]
    # Searching the IP Address (found in the ndiff) in the last generated scan file (scan-prev.xml)
    # Since ndiff gives only the difference between two scan files,
    #   if the difference found does not affect all the columns, the ndiff result will contains only that modified column
    #   And all the other unmodified columns will disappear from the ndiff file
    #   So, it's important to get all the columns of the modified row even if the modification affects one column
    #   This will prevents from getting a HTML row table that contains only the modified columns (the other unchanged columns will be empty)
    # XML Scan Tree : /nmaprun/host/address
    resultAddresses=nmaprun[0].xpath("host/address[@addr='"+address+"']")
    # If the search of the IP Address succeeded in the last generated scan file
    if len(resultAddresses)>0:
      # For each result line related of this search
      for resultAddress in resultAddresses:
        # Getting the parent base node (parent of the address node)
        # XML Scan Tree : /nmaprun/host
        resultNode=resultAddress.getparent()
        # Getting the ports of the current host from the Scan file
        # XML Scan Tree : /nmaprun/host/ports/port
        resultPorts=resultNode.xpath("ports/port")
        # For each port
        for resultPort in resultPorts:
          # If the port does not exists in the list of "ports already found", we add it in this list
          # Because
          # -- The ndiff file contains only the modified ports and does not contain the unmodified ports (state=up already)
          # -- The scan file contains only the current found ports and does not contain the previous ports (from the previous scan)
          # -- The ndiff file and scan file can contains the same ports
          # So, we should exploit the scan file and the ndiff file together and we should only use each port once from the scan file and the ndiff file without dupplications
          if resultPort.get("portid")+"/"+resultPort.get("protocol") not in portsFinished:
            # Appending the port to the "ports already found" list
            portsFinished.append(resultPort.get("portid")+"/"+resultPort.get("protocol"))

    # IP Address of the current host added to the current HTML row table
    scan_result_obj_json['address']=address

    # Hostname array
    hostnameArray=[]
    # Hostname type array
    hostnameTypeArray=[]
    # Hostname node (the same hostname found in the previous scan)
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/hostnames
    hostnames=host.xpath("hostnames")
    # For each hostname
    for hostname in hostnames:
      # Appending the hostname to the hostname array
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/hostnames[name]
      hostnameArray.append(hostname[0].get("name"))
      # Appending the hostname type to the hostname type array
      # This hostname is the same hostname found in the previous scan
      hostnameTypeArray.append('same')
    # For each hostname (a new detected hostname from the previous scan)
    hostnames=host.xpath("hostnames/b")
    # For each hostname
    for hostname in hostnames:
      # Appending the hostname to the hostname array
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/hostnames/b[name]
      hostnameArray.append(hostname[0].get("name"))
      # Appending the hostname type to the hostname type array
      # This hostname is a new detected hostname from the previous scan
      hostnameTypeArray.append('added')
    # For each hostname (a removed hostname from the previous scan)
    hostnames=host.xpath("hostnames/a")
    # For each hostname
    for hostname in hostnames:
      # Appending the hostname to the hostname array
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/hostnames/a[name]
      hostnameArray.append(hostname[0].get("name"))
      # Appending the hostname type to the hostname type array
      # This hostname is a removed hostname from the previous scan
      hostnameTypeArray.append('removed')

    # Hostname object array that will be set in the current HTML row table
    hostname_final=[]
    # If the search of the IP Address succeeded in the last generated scan file
    if len(resultAddresses)>0:
      # For each result line related of this search
      for resultAddress in resultAddresses:
        # Getting the parent base node (parent of the address node)
        # XML Scan Tree : /nmaprun/host
        resultNode=resultAddress.getparent()
        # Getting the hostname of the current host from the Scan file
        # XML Scan Tree : /nmaprun/host/hostnames/hostname
        resultHostnames=resultNode.xpath("hostnames/hostname")
        # For each hostname
        for resultHostname in resultHostnames:
          # if the hostname already exists in the hostname array
          # XML Scan Tree : /nmaprun/host/hostnames/hostname[name]
          if resultHostname.get("name") in hostnameArray:
            # Searching for the hostname index in the hostname array
            hostnameIndex=hostnameArray.index(resultHostname.get("name"))
            # If the hostname type related to the current hostname (using the same hostname index) is the same as the previous scan
            if hostnameTypeArray[hostnameIndex]=='same':
              # Setting the hostname object
              hostname_final.append({'hostname':resultHostname.get("name"),'prepend':"",'td_style':""})
            # If the hostname type related to the current hostname (using the same hostname index) is a new hostname from the previous scan
            elif hostnameTypeArray[hostnameIndex]=='added':
              # Setting the hostname object
              hostname_final.append({'hostname':resultHostname.get("name"),'prepend':NotifyIfNewHostnameIsDetectedStr,'td_style':" style='color:green'"})
            # If the hostname type related to the current hostname (using the same hostname index) is a deleted hostname from the previous scan
            elif hostnameTypeArray[hostnameIndex]=='removed':
              # Setting the hostname object
              hostname_final.append({'hostname':resultHostname.get("name"),'prepend':"",'td_style':" style='color:red'"})
          # if the hostname index does not exist in the hostname array
          else:
            # Setting the hostname object
            hostname_final.append({'hostname':resultHostname.get("name"),'prepend':"",'td_style':""})
        break

    # Hostname of the current host added to the current HTML row table
    scan_result_obj_json['hostname']=hostname_final

    # The status of the current host
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/status
    state=host.xpath("status")
    # If the status node exists
    if len(state)>0:
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/status[state]
      state=state[0].get("state")
    # If the status node does not exist
    else:
      # If the search of the IP Address succeeded in the last generated scan file
      if len(resultAddresses)>0:
        # For each result line related of this search
        for resultAddress in resultAddresses:
          # Getting the parent base node (parent of the address node)
          # XML Scan Tree : /nmaprun/host
          resultNode=resultAddress.getparent()
          # Getting the status of the current host from the Scan file
          # XML Scan Tree : /nmaprun/host/status
          resultStatus=resultNode.xpath("status")
          # if the status node exists
          if len(resultStatus)>0:
            # XML Scan Tree : /nmaprun/host/status[state]
            state=resultStatus[0].get("state")
          break
      # If the search of the IP Address does fail in the last generated scan file
      else:
        # The host must be available (I forget why I set it like that)
        state="up"
    # Hostname of the current host added to the current HTML row table
    scan_result_obj_json['state']=state

    # OS Match array
    osmatchArray=[]
    # OS Match type array
    osmatchTypeArray=[]
    # The OS information of the current host (the same OS found in the previous scan)
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/os/osmatch
    osmatches=host.xpath("os/osmatch")
    # For each OS Match
    for osmatch in osmatches:
      # Appending the OS Match name found in the OS Match array
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/os/osmatch[name]
      osmatchArray.append(osmatch.get("name"))
      # This is the same OS found in the previous scan
      osmatchTypeArray.append('same')
    # The OS information of the current host (a new detected os from the previous scan)
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/os/b/osmatch
    osmatches=host.xpath("os/b/osmatch")
    # For each OS Match
    for osmatch in osmatches:
      # Appending the OS Match name found in the OS Match array
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/os/b/osmatch[name]
      osmatchArray.append(osmatch.get("name"))
      # This is a new detected os from the previous scan
      osmatchTypeArray.append('added')
    # The OS information of the current host (a removed os from the previous scan)
    # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/os/a/osmatch
    osmatches=host.xpath("os/a/osmatch")
    # For each OS Match
    for osmatch in osmatches:
      # Appending the OS Match name found in the OS Match array
      # XML Ndiff Tree : /nmapdiff/scandiff/hostdiff/(a/|b/|)host/os/a/osmatch[name]
      osmatchArray.append(osmatch.get("name"))
      # This is a removed os from the previous scan
      osmatchTypeArray.append('removed')

    # OS object array that will be set in the current HTML row table
    os_final=[]
    # If the search of the IP Address succeeded in the last generated scan file
    if len(resultAddresses)>0:
      # For each result line related of this search
      for resultAddress in resultAddresses:
        # Getting the parent base node (parent of the address node)
        # XML Scan Tree : /nmaprun/host
        resultNode=resultAddress.getparent()
        # Getting the OS Match of the current host from the Scan file
        # XML Scan Tree : /nmaprun/host/os/osmatch
        resultOsmatches=resultNode.xpath("os/osmatch")
        # For each OS Match
        for resultOsmatch in resultOsmatches:
          # If the OS Match exists in the OS Match array
          # XML Scan Tree : /nmaprun/host/os/osmatch[name]
          if resultOsmatch.get("name") in osmatchArray:
            # Searching for the OS Match index in the OS Match array
            osmatchIndex=osmatchArray.index(resultOsmatch.get("name"))
            # If the OS Match type related to the current OS Match (using the same OS Match index) is the same as the previous scan
            if osmatchTypeArray[osmatchIndex]=='same':
              # Setting the OS Match object
              os_final.append({'os':resultOsmatch.get("name"),'prepend':"",'td_style':""})
            # If the OS Match type related to the current OS Match (using the same OS Match index) is a new OS Match from the previous scan
            elif osmatchTypeArray[osmatchIndex]=='added':
              # Setting the OS Match object
              os_final.append({'os':resultOsmatch.get("name"),'prepend':NotifyIfNewOSInfoIsDetectedStr,'td_style':" style='color:green'"})
            # If the OS Match type related to the current OS Match (using the same OS Match index) is a deleted OS Match from the previous scan
            elif osmatchTypeArray[osmatchIndex]=='removed':
              # Setting the OS Match object
              os_final.append({'os':resultOsmatch.get("name"),'prepend':"",'td_style':" style='color:red'"})
          # if the OS Match index does not exist in the OS Match array
          else:
            # Setting the OS Match object
            os_final.append({'os':resultOsmatch.get("name"),'prepend':"",'td_style':""})
        break
    # OS of the current host added to the current HTML row table
    scan_result_obj_json['os']=os_final

    # Ports object array that will be set in the current HTML row table
    ports_final=[]
    # If the search of the IP Address succeeded in the last generated scan file
    if len(resultAddresses)>0:
      # For each result line related of this search
      for resultAddress in resultAddresses:
        # Getting the parent base node (parent of the address node)
        # XML Scan Tree : /nmaprun/host
        resultNode=resultAddress.getparent()
        # Getting the ports of the current host from the Scan file
        # XML Scan Tree : /nmaprun/host/ports/port
        resultPorts=resultNode.xpath("ports/port")
        # For each port
        for resultPort in resultPorts:
          # If the port exists in the port array
          # XML Scan Tree : /nmaprun/host/ports/port[portid]
          # XML Scan Tree : /nmaprun/host/ports/port[protocol]
          if (resultPort.get("portid")+"/"+resultPort.get("protocol")) in portArray:
            # Searching the index of the port in the port array
            portIndex=portArray.index(resultPort.get("portid")+"/"+resultPort.get("protocol"))
            # If the port (using the port index) is the same as the detected port in the previous scan
            if portTypeArray[portIndex]=='same':
              # Setting the port object
              ports_final.append({'number':resultPort.get("portid"),'proto':resultPort.get("protocol"),'state':portStateArray[portIndex],'service':portServiceArray[portIndex],'version':portVersionArray[portIndex],'td_style':""})
            # If the port (using the port index) is a new detected port from the previous scan
            elif portTypeArray[portIndex]=='added':
              # Setting the port object
              ports_final.append({'number':resultPort.get("portid"),'proto':resultPort.get("protocol"),'state':portStateArray[portIndex],'service':portServiceArray[portIndex],'version':portVersionArray[portIndex],'prepend':NotifyIfNewPortUpIsDetectedStr,'td_style':" style='color:green'"})
            # If the port (using the port index) is a removed port from the previous scan
            elif portTypeArray[portIndex]=='removed':
              # Setting the port object
              ports_final.append({'number':resultPort.get("portid"),'proto':resultPort.get("protocol"),'state':portStateArray[portIndex],'service':portServiceArray[portIndex],'version':portVersionArray[portIndex],'prepend':NotifyIfNewPortDownIsDetectedStr,'td_style':" style='color:red'"})
          # If the port doesn't exist in the port array
          else:
            # The port service node
            # XML Scan Tree : /nmaprun/host/ports/port/service
            portService=resultPort.xpath("service")
            # The variable that will contains the port service value
            portServiceVal=""
            # The variable that will contains the port version value
            portVersion=""
            # If the port service node exists
            if len(portService)>0:
              # The port service name value
              # XML Scan Tree : /nmaprun/host/ports/port/service[name]
              portServiceVal=portService[0].get("name")
              # If the port product is detected
              if portService[0].get("product"):
                # Adding the product attribute to the variable that will be stored later
                portVersion=portVersion+portService[0].get("product")+" "
              # If the port version is detected
              if portService[0].get("version"):
                # Adding the version attribute to the variable that will be stored later
                portVersion=portVersion+portService[0].get("version")+" "
              # If the port extrainfo is detected
              if portService[0].get("extrainfo"):
                # Adding the extrainfo attribute to the variable that will be stored later
                portVersion=portVersion+"("+portService[0].get("extrainfo")+") "
            # Setting the port object
            ports_final.append({'number':resultPort.get("portid"),'proto':resultPort.get("protocol"),'state':resultPort.xpath("state")[0].get("state"),'service':portServiceVal,'version':portVersion,'td_style':""})
        break

    # In the previous bloc, the ports found are those from the scan file
    # Now, we add the missing ports. Not in the scan file but in the ndiff file
    # For each port element in the port array
    for idx,port in enumerate(portArray):
      # If the port is not in the "ports already found"
      if port not in portsFinished:
        # If the port is the same as the previous scan
        if portTypeArray[idx]=='added':
          # Green color row
          tdStyle2=" style='color:green'"
        # If the port is removed from the previous scan
        elif portTypeArray[idx]=='removed':
          # Red color row
          tdStyle2=" style='color:red'"
        # If the port is added from the previous scan
        else:
          # default row style
          tdStyle2=""
        # Setting the port object
        ports_final.append({'number':port.split('/')[0],'proto':port.split('/')[1],'state':portStateArray[idx],'service':portServiceArray[idx],'version':portVersionArray[idx],'td_style':tdStyle2})
    # Port of the current host added to the current HTML row table
    scan_result_obj_json['ports']=ports_final

    # Appending the current host object tot the current HTML row table
    scan_result_array_json.append(scan_result_obj_json)

# If this is the first scan :
# -- The ndiff file does not exist
# -- Or
# -- The XML Ndiff Tree does not exist : /nmapdiff/scandiff/hostdiff
else:
  # For each host
  for host in hosts:
    # Object that represents one row that contains a result line in the HTML table
    scan_result_obj_json={}
    # A prepended string that will be set when generating the HTML row table
    scan_result_obj_json['prepend']=NotifyIfNewHostUpIsDetectedStr
    # The CSS Style of this current row (green color)
    scan_result_obj_json['tr_style']=" style='color:green'"
    # Host node if this host is always available from the previous scan
    # XML Scan Tree : /nmaprun/host/ports/port
    ports=host.xpath("ports/port")
    # Addresses node of the current host
    # XML Scan Tree : /nmaprun/host/address
    addresses=host.xpath("address")
    # For each address node
    for address in addresses:
      # IP Address of the current host
      # XML Scan Tree : /nmaprun/host/address[addr]
      scan_result_obj_json['address']=address.get("addr")
    # Hostnames of the current host
    # XML Scan Tree : /nmaprun/host/hostnames/hostname
    hostnames=host.xpath("hostnames/hostname")
    # Hostnames object array that will be set in the current HTML row table
    hostnames_final=[]
    # For each hostname
    for hostname in hostnames:
      # Setting the port object
      hostnames_final.append({'hostname':hostname.get("name"),'prepend':NotifyIfNewHostnameIsDetectedStr,'td_style':""})
    # IP Address of the current host added to the current HTML row table
    scan_result_obj_json['address']=hostnames_final
    # Statuses of the current host
    # XML Scan Tree : /nmaprun/host/status
    statuses=host.xpath("status")
    # For each status
    for status in statuses:
      # State of the current host
      # XML Scan Tree : /nmaprun/host/status[state]
      scan_result_obj_json['state']=status.get("state")

    # OS Match of the current host
    # XML Scan Tree : /nmaprun/host/os/osmatch
    osmatches=host.xpath("os/osmatch")
    # OS object array that will be set in the current HTML row table
    os_final=[]
    # For each OS Match
    for osmatch in osmatches:
      # Setting the port object
      os_final.append({'os':osmatch.get("name"),'prepend':NotifyIfNewOSInfoIsDetectedStr,'td_style':""})
    # OS of the current host added to the current HTML row table
    scan_result_obj_json['os']=os_final

    # Ports object array that will be set in the current HTML row table
    ports_final=[]
    # If the ports node exists
    if len(ports)>0:
      # For each port node
      for port in ports:
        # Port service node of the current host
        # XML Scan Tree : /nmaprun/host/ports/port/service
        serices=port.xpath("service")
        # Port service value
        portServiceStr=""
        # For each service
        for service in serices:
          # XML Scan Tree : /nmaprun/host/ports/port/service[name]
           portServiceStr=portServiceStr+service.get("name")+" "
        # For each service
        for service in serices:
          # Port service version value
          portVersionStr=""
          # XML Scan Tree : /nmaprun/host/ports/port/service[product]
          if service.get("product"):
            # Adding the product attribute to the variable that will be stored later
            portVersionStr=portVersionStr+service.get("product")+" "
          # XML Scan Tree : /nmaprun/host/ports/port/service[version]
          if service.get("version"):
            # Adding the version attribute to the variable that will be stored later
            portVersionStr=portVersionStr+service.get("version")+" "
          # XML Scan Tree : /nmaprun/host/ports/port/service[extrainfo]
          if service.get("extrainfo"):
            # Adding the extrainfo attribute to the variable that will be stored later
            portVersionStr=portVersionStr+"("+service.get("extrainfo")+") "
          # Setting the port object
          ports_final.append({'number':port.get("portid"),'proto':port.get("protocol"),'state':port.xpath("state")[0].get("state"),'service':portServiceStr,'version':portVersionStr,'prepend':NotifyIfNewPortUpIsDetectedStr,'td_style':""})
    # Ports of the current host added to the current HTML row table
    scan_result_obj_json['ports']=ports_final


html=""
html=html+"To: "+To+"\n"
html=html+"From: "+From+"\n"
html=html+"Subject: Scan report"+"\n"
html=html+"Content-Type: text/html"+"\n"
html=html+"\n"


html=html+"<html><head><style>"
html=html+"table {border-collapse: separate;border-spacing: 0;}"
html=html+"th,td {padding: 3px 5px}"
html=html+"th {background: #395870;font-weight: bold;;color:white;border: 1px gray solid; background: linear-gradient(#49708f, #293f50);}"
html=html+"th:first-child {border-top-left-radius: 5px;text-align: left;}"
html=html+"th:last-child {border-top-right-radius: 5px;}"
html=html+"td {border: 1px solid #cecfd5;}"
html=html+"td:first-child {border-left: 1px solid #cecfd5;}"
html=html+"</style></head><body><table>"
html=html+"<tr><th rowspan='2'>IP Address</th><th rowspan='2'>Hostname</th><th rowspan='2'>State</th><th colspan='4'>Ports</th><th rowspan='2'>OS</th></tr>"
html=html+"<tr><th>Number</th><th>State</th><th>Service</th><th>Version</th></tr>"
html=html+NotifyAlwaysAfterScanIsFinishedStr

result_green_tr=[x for x in scan_result_array_json if x['tr_style'] == " style='color:green'"]
result_red_tr=[x for x in scan_result_array_json if x['tr_style'] == " style='color:red'"]
result_other_tr=[x for x in scan_result_array_json if x['tr_style'] != " style='color:red'" and x['tr_style'] != " style='color:green'"]

def filter_port(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

result_green_port=[x for x in result_other_tr if filter_port(x['ports'],lambda y: y['td_style'] == " style='color:green'")==True]
result_other_port=[x for x in result_other_tr if filter_port(x['ports'],lambda y: y['td_style'] == " style='color:green'")==False]
result_other_red_port=[x for x in result_other_port if filter_port(x['ports'],lambda y: y['td_style'] == " style='color:red'")==True]
result_other_other_port=[x for x in result_other_port if filter_port(x['ports'],lambda y: y['td_style'] == " style='color:red'")==False]

scan_result_array_json2=result_green_tr + result_green_port +  result_other_other_port + result_other_red_port + result_red_tr

for host in scan_result_array_json2:
  commonLines=str(len(host['ports']))
  showLine=False
  tr_prepend=""
  htmlLine=""
  if 'prepend' in host:
    tr_prepend=host['prepend']
  htmlLine=htmlLine+tr_prepend
  tr_style=""
  if 'tr_style' in host:
    tr_style=host['tr_style']
  if ShowNewHostUp is None or (ShowNewHostUp and ShowNewHostUp=="true" and tr_style==" style='color:green'"):
    showLine=True
  if ShowNewHostDown is None or (ShowNewHostDown and ShowNewHostDown=="true" and tr_style==" style='color:red'"):
    showLine=True
  htmlLine=htmlLine+"<tr"+tr_style+">"
  htmlLine=htmlLine+"<td rowspan='"+commonLines+"'>"+host['address']+"</td>"
  htmlLine=htmlLine+"<td rowspan='"+commonLines+"'>"
  for hostname in host['hostname']:
    td_prepend=""
    if 'prepend' in hostname:
      td_prepend=hostname['prepend']
    htmlLine=htmlLine+td_prepend
    td_style=""
    if 'td_style' in hostname:
      td_style=hostname['td_style']
    if ShowNewHostnameInfo is None or (ShowNewHostnameInfo and ShowNewHostnameInfo=="true" and td_style!=""):
      showLine=True
    htmlLine=htmlLine+"<span"+td_style+">"+hostname['hostname']+"</span><br/>"
  htmlLine=htmlLine+"</td>"
  htmlLine=htmlLine+"<td rowspan='"+commonLines+"'>"+host['state']+"</td>"
  htmlTmp=""
  htmlTmp=htmlTmp+"<td rowspan='"+commonLines+"'>"
  for os in host['os']:
    td_prepend=""
    if 'prepend' in os:
      td_prepend=os['prepend']
    htmlTmp=htmlTmp+td_prepend
    td_style=""
    if 'td_style' in os:
      td_style=os['td_style']
    if ShowNewOSInfo is None or (ShowNewOSInfo and ShowNewOSInfo=="true" and td_style!=""):
      showLine=True
    htmlTmp=htmlTmp+"<span"+td_style+">"+os['os']+"</span><br/>"
  htmlTmp=htmlTmp+"</td>"
  i=0
  for port in host['ports']:
    if i>0:
      htmlLine=htmlLine+"</tr><tr"+tr_style+">"
    td_prepend=""
    if 'prepend' in port:
      td_prepend=port['prepend']
    htmlLine=htmlLine+td_prepend
    td_style=""
    if 'td_style' in port:
      td_style=port['td_style']
    if ShowNewPortUp is None or (ShowNewPortUp and ShowNewPortUp=="true" and td_style==" style='color:green'"):
      showLine=True
    if ShowNewPortDown is None or (ShowNewPortDown and ShowNewPortDown=="true" and td_style==" style='color:red'"):
      showLine=True
    htmlLine=htmlLine+"<td"+td_style+">"+port['number']+"/"+port['proto']+"</td>"
    htmlLine=htmlLine+"<td"+td_style+">"+port['state']+"</td>"
    htmlLine=htmlLine+"<td"+td_style+">"+port['service']+"</td>"
    htmlLine=htmlLine+"<td"+td_style+">"+port['version']+"</td>"
    if i==0:
      htmlLine=htmlLine+htmlTmp
    i=i+1
  htmlLine=htmlLine+"</tr>"
  if showLine:
    html=html+htmlLine



html=html+"</table>"
html=html+"</table>"
html=html+"<h5>Hosts changed state to available : "+str(len(result_green_tr))+"/"+str(len(scan_result_array_json))+"</h5>"
html=html+"<h5>Hosts changed state to unavailable : "+str(len(result_red_tr))+"/"+str(len(scan_result_array_json))+"</h5>"
html=html+"<h5>Hosts state already available : "+str(len(result_other_tr))+"/"+str(len(scan_result_array_json))+"</h5>"
html=html+"<h5>Start time : "+startTimeStr+"</h5>"
html=html+"<h5>End time : "+endTimeStr+"</h5>"
html=html+"<h5>Duration : "+duration+" seconds</h5>"
html=html+"</body></html>"
#print html

f=open(BaseDir+"/logs/mail_output.txt","w")
f.write(html)

