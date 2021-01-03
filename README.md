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

An optional feature of this script is termdown - the countdown feature. This is a visual countdown timer. Install:

<pre>pip install termdown</pre>

Github repo:

[Termdown - Github](https://github.com/trehn/termdown)

## Usage

The script must be run as root to modify the hosts file. 

<pre>sudo doenum.py -h</pre>

<pre>usage: doenum.py [-h] -t TARGET -d DIRECTORY -n NAME [-u USER]

Enumerate a host.

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        IP address of the host you want to enumerate
  -d DIRECTORY, --directory DIRECTORY
                        Specify the parent directory. "-d tryhackme" will
                        enter ~/tryhackme/ and create a directory structure
                        there.
  -n NAME, --name NAME  The name of the host. This will be the child directory
                        created and will be added to /etc/hosts
  -u USER, --user USER  Set your current user. If not set, it will take the
                        user out of the absolute path (/home/user/..). User
                        will be root if script is confused.
</pre>

<pre>sudo doenum.py -t TARGET -d DIRECTORY -n NAME -u USER</pre>

The script will create a directory for the specified /directory/name.

Example:

<pre>sudo enumerate.py -i 10.10.10.10 -d /home/user/hackthebox -n boxname -u user</pre>

The directory structure:

<pre>
/home/user/hackthebox/boxname
├── nmap
│   └── nmap.out
└── wfuzz
    └── wfuzz.out:80
    └── wfuzz.out:8080</pre>

