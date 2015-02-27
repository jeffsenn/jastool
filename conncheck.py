import socket, thread, time, select, sys

ROUTER="192.168.1.1"
TEST_URL="/images/empty.gif"
DEBUG=False
SOCK_TIMEOUT=5.0
STAT_FILE = "/run/conncheck.dat"

def now():
    return int(round(time.time()))

def test_connect(hp, timeout=2.0):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(hp)
    except:
        return 0, now()                    
    return 1, now()

def test_http(host=ROUTER,url=TEST_URL,port=80,timeout=SOCK_TIMEOUT):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host,port))
    except:
        if DEBUG: print "CONNECT FAIL"
        return 0, now()                    
    s.send("GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (url,host))
    later = now() + timeout
    response = ''
    while now() < later:
        r,w,e = select.select([s],[],[],1)
        if s in r:
            response += s.recv(1000)
            if response.startswith("HTTP"):
                return 1, now()
    if DEBUG: print "NO RESPONSE"
    return 0,int(round(now()))

if __name__ == '__main__':
    import sys
    DEBUG = "-debug" in sys.argv
    worked, t = test_http()
    if DEBUG: print worked,t
    try:
        # status file is: FAIL_TIME FIRST_FAILTIME FAIL_CNT succeed... toggle
        stat = map(int,open(STAT_FILE,'rb').read().split(" "))
    except:
        stat = None
    if stat is None or len(stat) != 9:
        if worked:
            stat = [0,0,0, t,t,0, 0,0,0]
        else:
            stat = [t,t,0, 0,0,0, 0,0,0]
    if DEBUG: print "STAT", stat
    if worked:
        stat[2] = 0
        if stat[5] == 0:
            stat[4] = t
        stat[5] += 1
        stat[3] = t
    else:
        stat[5] = 0
        if stat[2] == 0:
            stat[1] = t
        stat[2] += 1
        stat[0] = t
    if DEBUG: print "STAT", stat
    
    if stat[2] > 2 and (stat[1]-stat[0]) > 45:
        # more than 2 failures in a row for more than 45 seconds
        tt = now()
        if tt - stat[7] > 300: # only toggle every 5 minutes
            print "TOGGLE ROUTER"
            try:
                import toggle
                toggle.toggle(1, 2.0)
                if stat[8] == 0:
                    stat[7] = tt
                stat[8] += 1
                stat[7] = tt
            except:
                print "TOGGLE FAIL"
        else:
            print "TOGGLE SKIP too soon",tt

    open(STAT_FILE,'wb').write("%d %d %d %d %d %d %d %d %d" % tuple(stat))
        
    
    
