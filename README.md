# Do Enum

A script that does all the initial enumeration for you.

 - Add IP and domain to hosts file
 - Create an organised directory structure
 - Run a portscan with nmap's python3-nmap
 - A web directory scan if port 80 or 8080 is open with Wfuzz

## Requirements

This script requires the following python3 modules:

 - python3-nmap
 - pprint

## Usage

The script must be run as root to modify the hosts file. 

<pre>sudo enumerate.py -i IP -d DIRECTORY -n NAME</pre>

The script will create a directory for the specified directory/name.

Example:

<pre>sudo enumerate.py -i 10.10.10.10 -d /home/user/hackthebox -n boxname</pre>

The directory structure:

<pre>
/home/user/tryhackme/hells
├── nmap
│   └── nmap.out
└── wfuzz
    └── wfuzz.out:80</pre>


