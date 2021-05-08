from urllib import urlopen
import sys, commands

entry_by = sys.argv[1]
web_page = sys.argv[2]

ip_local=commands.getoutput('hostname -I')

url_remote="https://helloworld.co.in/earthrover/run.php?entry_by=" + entry_by + "&url=" + web_page + "&ip_local=" + ip_local

urlopen(url_remote)
