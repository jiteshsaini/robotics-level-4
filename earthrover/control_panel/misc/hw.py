import sys, commands, os

entry_by = sys.argv[1]
web_page = sys.argv[2]
ip_local=commands.getoutput('hostname -I')

parameters="p="+entry_by+"*"+web_page+"*"+ip_local
url_remote="https://helloworld.co.in/deploy/run.php?" + parameters
cmd="curl -s " + url_remote
result=os.popen(cmd).read()
