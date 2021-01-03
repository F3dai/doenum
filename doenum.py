import sys
import os

import nmap3
import argparse

import subprocess
import shutil
import pprint

# Working Directories #
nmapDirectory = '/nmap/'
wfuzzDirectory = '/wfuzz/'

# Wfuzz Wordlist #
wfuzzList = "/usr/share/wordlists/wfuzz/general/big.txt" # Confirm this is true
wfuzzIgnore = "404,403,301"

# Port ranges #
httpTopPort = 8999
httpLowPort = 8000
httpStandardPorts = (80, 443)

# Count Down #
countSeconds = 5 # Set to 0 for none

# Parse Arguments #

def parseArgs():
	global targetIP, targetDirectory, targetName, user

	parser = argparse.ArgumentParser(description='Enumerate a host.')

	parser.add_argument('-t', '--target', required=True, help='IP address of the host you want to enumerate')
	parser.add_argument('-d', '--directory', required=True, help='Specify the parent directory. "-d tryhackme" will enter ~/tryhackme/ and create a directory structure there.')
	parser.add_argument('-n', '--name', required=True, help='The name of the host. This will be the child directory created and will be added to /etc/hosts')
	parser.add_argument('-u', '--user', required=False,	help='Set your current user for setting permissions. If not set, it will take the user from the absolute path (/home/user/..). User will be root if script is confused.')
	args = parser.parse_args()

	targetIP = args.target
	targetDirectory = args.directory + "/"
	targetName = args.name

	# Grab home directory as user
	# Script runs as root - assume the user given their parent directory?

	if not args.user:
		user = targetDirectory.split('/')
		if user[1] == "root":
			user = "root"
		else:
			user = user[2]
	else:
		user = args.user

# Count down

def countdown():
	try:
		subprocess.call(['termdown', str(countSeconds)])
	except:
		print("\t[!] Termdown not installed. Install with 'pip install termdown'")

# Edit /etc/hosts #

def echoHost():
	hostFilePath = "/etc/hosts"
	hostsFileRead = open(hostFilePath).read()
	# Checks if IP in system's hosts file
	if targetIP in hostsFileRead or targetName in hostsFileRead:
		if input("[!] Entry exists in hosts, reset file? (y/n) ") == "y":
			# Read original hosts
			with open(".hosts","r") as hostBackup:
				hostBackupLines = hostBackup.read()
			# Replace current hosts
			try:
				with open(hostFilePath, "w+") as hostFile:
					for line in hostBackupLines:
						hostFile.write(line)
					print("\t[+] Reset " + hostFilePath)
			except:
				print("[-] Exiting... Run as root")
				exit()
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
			print("k")
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

def wfuzz(port):
	print("\n[!] Starting Wfuzz scan...\n")
	wfuzzOut = workDirectory + wfuzzDirectory + "wfuzz.out"
	subprocess.call(["wfuzz", "-w", wfuzzList, "--hc", wfuzzIgnore, "-u", targetIP + ":" + port + "/FUZZ", "-c", "-f", wfuzzOut + "-" + port])
	print("\t[+] Web directory scannining done for port " + port)

# Scan HTTP #

def checkRange(ports):
	toScan = [] # Init empty array for ports in http range
	for port in ports:
		# Check if standard http or in 8k range.
		if httpLowPort <= int(port) <= httpTopPort or int(port) in (httpStandardPorts):
			wfuzz(port)

# Change File Ownership #

def setPermissions():
	subprocess.call(['chown', '-R' , user + ':' + user, workDirectory])
	print("\t[+] Set file structure ownership to '{}'".format(user))


def main():

	args = parseArgs() # Accept params

	countdown() # termdown visual timer

	echoHost() # Add name.host to /etc/hosts

	createStructure() # Create project directory

	ports = portscan(targetIP) # Port Scan returns list of open ports

	checkRange(ports) # Check for common http ports

	# To do:
	# - Run nikto if http open too...
	# - Check windows ports? enum4ilnux...
	# - Ensure dir perms with exception handling. i.e ctrl+c -> set perms
	# - Copy hosts file before running instead of replacing with .hosts?

	setPermissions() # permz innit

	print("\n## Done ##")

# start #

if __name__ == '__main__':

	main()