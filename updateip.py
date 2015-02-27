import urllib2, socket, json, subprocess
DEBUG=True
HOST=None
IP=None

from secrets import MAYA_NS
SERVER, DEFAULT_DOMAIN, KEY = MAYA_NS

IP_SERVERS=(('http://jsonip.com','ip'),('http://ip-api.com/json','query'))

def nslookup(host,server):
        p= subprocess.Popen(["nslookup",host,server], close_fds=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        result = p.communicate()[0]
        result = result.split("Address:")
        h = result[-2].strip().split()[-1]
        i = result[-1].strip()
        if h == host: return i
        return None

def updateNS(server, host, current_ip = None, secret=KEY):
    result = None
    if current_ip is None:
        for retries in xrange(4,0,-1):
            for url,attr in IP_SERVERS:
                try:
                    httpResponse = urllib2.urlopen(urllib2.Request(url)).read()
                    break
                except:
                    if retries == 1:
                        raise
        jsonData = json.loads(httpResponse)
        current_ip = jsonData[attr]
    try:
        named_ip = nslookup(host,server)
        if DEBUG: print "NSLOOKUP",named_ip
    except:
        named_ip = None
    if named_ip is None:
        # this is not as reliable due to caching on many systems
        try:
            named_ip = socket.gethostbyname(host)
            if DEBUG: print "GETHOSTNAME",named_ip            
        except:
            named_ip = None
    if named_ip != current_ip:
        zone = host.split('.',1)[1]
        print "Updating",host,current_ip,named_ip
        op = "server %s\nzone %s\nkey %s %s\nupdate delete %s\nupdate add %s 86400 A %s\nsend\n\n" %(server,zone,zone,secret,host,host,current_ip)
        p= subprocess.Popen(["nsupdate"], close_fds=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.stdin.write(op)
        result = p.communicate()[0]
        if DEBUG and result != '': print "FAIL?=",result
    elif DEBUG:
        print "No update necessary"
    return result

if __name__ == "__main__":
    import sys
    DEBUG = "-debug" in sys.argv
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    for a in argv:
        if a[0] in "0123456789":
            IP = a
        else:
            HOST=a
    if HOST is None:
        HOST=socket.gethostname().split('.')[0] + "." + DEFAULT_DOMAIN
        if DEBUG: print "DEFAULT HOST:", HOST
    updateNS(SERVER,HOST,IP)


