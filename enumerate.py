import sys
import os

import nmap3
import argparse

import subprocess
import shutil
import pprint

# Working Directories #
nmapDirectory = "/nmap/"
wfuzzDirectory = '/wfuzz/'
# Wfuzz Wordlist #
wfuzzList = "/usr/share/wordlists/wfuzz/general/big.txt" # Confirm this is true
wfuzzPorts = "404,403,301"

# Count Down #
countSeconds = 1 # Set to 0 for none

# Parse Arguments #

def parseArgs():
	global targetIP, targetDirectory, targetName, user
	parser = argparse.ArgumentParser(description='Enumerate a host.')
	parser.add_argument('-i', '--ip', required=True,
		help='IP address of the host you want to enumerate')
	parser.add_argument('-d', '--directory', required=True,
		help='Specify the parent directory. "-d tryhackme" will enter ~/tryhackme/ and create a directory structure there.')
	parser.add_argument('-n', '--name', required=True,
		help='The name of the host. This will be the child directory created and will be added to /etc/hosts')
	args = parser.parse_args()

	targetIP = args.ip
	targetDirectory = args.directory
	targetName = args.name

	# Grab home directory as user
	# Script runs as root - assume the user given their parent directory?s

	user = targetDirectory.split('/')
	if user[1] == "root":
		user = "root"
	else:
		user = user[2]

# Count down

def countdown():
	subprocess.call(['termdown', str(countSeconds)])

# Edit /etc/hosts #

def echoHost():
	hostFilePath = "/etc/hosts"
	# Checks if IP in hosts
	if targetIP or targetName in open("/etc/hosts").read():
		if input("[!] Entry exists in hosts, reset file? (y/n) ") == "y":
			# Read original hosts
			with open(".hosts","r") as hostBackup:
				hostBackupLines = hostBackup.read()
			# Replace current hosts
			with open(hostFilePath, "w+") as hostFile:
				for line in hostBackupLines:
					hostFile.write(line)
				print("\t[+] Reset " + hostFilePath)
		else:
			print("[!] Ok, adding it in anyway. Beware of conflicts.")
	with open(hostFilePath,"a+") as hostFile:
		try:
			hostFile.write(targetIP + "\t" + targetName + ".host\n")
			print("\t[+] Added {} as {}.host to {}".format(targetIP, targetName, hostFilePath))
		except:
			print("[!] Run script as root")
			exit()

# File Structure #

def createStructure():
	global workDirectory
	workDirectory = targetDirectory + "/" + targetName
	projectExists = os.path.exists(workDirectory)
	if projectExists:
		if input("[!] Project exists. Delete and overwrite? (y/n) ") == "y":
			shutil.rmtree(workDirectory)
			print("\t[+] Deleted " + workDirectory)
		else:
			print("you're gay!")
			exit()
	os.mkdir(workDirectory)
	print("\t[+] Created parent directory: " + workDirectory)
	os.mkdir(workDirectory + wfuzzDirectory)
	print("\t[+] Created " + wfuzzDirectory)
	os.mkdir(workDirectory + nmapDirectory)
	print("\t[+] Created " + nmapDirectory)

# nmap scan #

def portscan(ip):
	# Initialise variables
	nmapOut = targetDirectory + targetName + nmapDirectory + "nmap.out"
	ports = [] 
	nmap = nmap3.NmapScanTechniques()

	print("\n## Starting nmap scan ##\n")
	results = nmap.nmap_syn_scan(ip) # nmap scan all ports

	# Write to nmap log file in dir structure
	with open(nmapOut, "w") as nmapOutFile:
		pprint.pprint(results, nmapOutFile)

	# Print open ports to screen
	for ip in results:
		for port in results[ip]:
			try:
				print(port['portid'], port['state'])
				ports.append(port['portid'])
			except:
				pass
	return ports

# web scan #

def wfuzz(ports):
	wfuzzOut = workDirectory + wfuzzDirectory + "wfuzz.out"
	for port in ports:
		subprocess.call(["wfuzz", "-w", wfuzzList, "--hc", wfuzzPorts, "-u", targetIP + "/FUZZ:" + port, "-c", "-f", wfuzzOut + "-" + port])
		print("\t[+] Web directory scannining done for port " + port)

# Change File Ownership #

def setPermissions():
	subprocess.call(['chown', '-R' , user + ':' + user, workDirectory])
	print("\t[+] Set file structure ownership to '{}'".format(user))

# start #

if __name__ == '__main__':

	args = parseArgs() # Accept params

	countdown()

	echoHost() # Add name.host to /etc/hosts

	createStructure() # Create project directory

	ports = portscan(targetIP) # Port Scan returns list of open ports

	if "80" in ports:
		if input("\n[!] Common web ports found. Perform web directory scan? (y/n) ") == "y":
			print()
			wfuzz(["80", "8080"]) # Web Directory Scan
	#if "443" in ports:
	#	enum4linux()

	setPermissions()

	print("\n## Done ##")
