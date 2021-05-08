from urllib import urlopen
import sys

entry_by = sys.argv[1]
url_local = sys.argv[2]

url_remote="https://helloworld.co.in/earthrover/run.php?entry_by=" + entry_by + "&url=" + url_local

urlopen(url_remote)

print (">>>>")
