#!/usr/bin/env python3

# Li Yuan, ADSC, 2018
#from pwn import ssh
import csv
import sys

#input object
class Item:

	def __init__(self, switch, port, type1,comment):
		self.Switch = switch
		self.Port = port
		self.Type = type1
		self.Comment = comment
#output object	
class OutputItem:
	def __init__(self,type1,switch,slot,port, pvid, untagged, tagged,comment):
		self.Type=type1
		self.Switch=switch
		self.Slot=slot
		self.Port=port
		self.Pvid=pvid
		self.Untagged=untagged
		self.Tagged=tagged
		self.Comment=comment
		
	


def readInputFile(fname):

	List=list()
	with open(fname) as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			newItem=Item(row['Switch'], row['Port'], row['Type'],row['Comment'])
			List.append(newItem)
	return List
    


	
def generateOutput(List):
	VLanCount=1;
	OutputList=list()
	for item in List:
		if item.Type=="1":
			VLanCount+=1
			output=OutputItem(1,item.Switch,"1",item.Port,str(VLanCount),str(VLanCount),"",item.Comment)
			OutputList.append(output)
		elif item.Type=="0":
			output=OutputItem(0,item.Switch,"1",item.Port,"1","1","",item.Comment)
			OutputList.append(output)
	#generate vlan string(1,2,3,4....) for normal nodes
	allVLan=""
	serverVLanCount=VLanCount		
	while (VLanCount>0):
		if allVLan =="":
			allVLan=str(VLanCount)
		else:
			allVLan=allVLan+","+str(VLanCount)
		VLanCount-=1
	#generate vlan string(2,3,4....) for server nodes
	serverVLan=""		
	while (serverVLanCount>1):
		if serverVLan =="":
			serverVLan=str(serverVLanCount)
		else:
			serverVLan=serverVLan+","+str(serverVLanCount)
		serverVLanCount-=1
	for item in List:
		if item.Type=="2":
			output=OutputItem(2,item.Switch,"1",item.Port,"1","1",serverVLan,item.Comment)
			OutputList.append(output)
		elif item.Type=="3":
			output=OutputItem(3,item.Switch,"1",item.Port,"1","",allVLan,item.Comment)
			OutputList.append(output)
	return OutputList
		
		
	
def writeToFile(List):
	file = open("output.csv","w")
	file.write("Switch;Slot;Port;PVID;Untagged VLAN;Tagged VLAN;Comment\n")
	for outputItem in List:
		file.write(outputItem.Switch+";"+outputItem.Slot+";"+outputItem.Port+";"+outputItem.Pvid+";"+outputItem.Untagged+";"+outputItem.Tagged+";"+outputItem.Comment+"\n")
	file.close() 
fname = 'analyzerInput.csv'
if len(sys.argv)>1:
    fname = sys.argv[1]
List=readInputFile(fname)
outputList=generateOutput(List)
writeToFile(outputList)
